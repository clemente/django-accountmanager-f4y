from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.validation import Validation
from accounts.models import Account, Transaction, ALLOWED_CURRENCIES
from accounts.currency import currency_rate
import datetime
from decimal import Decimal
import re


ERROR_CODES = {
    'm_par': 'Missing parameters',
    'm_destacc': "Missing destination account",
    'm_srcacc': "Missing source account",
    'm_am': "Missing amount",
    'm_cur': "Missing currency",
    'nf_cur': "Currency not supported",
    'nf_acc': "Account doesn't exist",
    'z_srcacc': "Source account would have negative balance",
    'z_destacc': "Destination account would have negative balance",
    'no_same': "Can't transfer to same account",
    'no_number': "Not a valid number",
}

def extract_error_code_from_bundle(errors):
    """From a tastypie "errors" dict, return the error code of 1 error message. It returns error code (not message) from our table. It discards other errors if there are >1. It can handle different input formats."""
    # Normalize errors. The ones from validator are "{transactions: {…}}", the ones from obj_create are "{…}", the ones from models are "{error:…}"
    # print(type(errors))
    # print(errors)
    if 'transactions' in errors:
        errors=errors['transactions']
    elif 'accounts' in errors:
        errors=errors['accounts']
    elif 'error' in errors:
        errors=errors['error']
    # print(type(errors))
    # print(errors)
    if isinstance(errors,dict):
        # the "errors" dict could have many errors but our response format mandates to tell only one. So we take any of them
        error_msg=next(iter(errors.values())) # details: https://stackoverflow.com/questions/3097866/access-an-arbitrary-element-in-a-dictionary-in-python
    elif isinstance(errors,str):
        error_msg=re.sub("^\['","",errors)
        error_msg=re.sub("'\]$","",error_msg)
    else:
        raise NotImplementedError()

    assert isinstance(error_msg,str) # We have 1 and only 1 message
        

    #import ipdb; ipdb.set_trace()

    codes_for_msg=[k for k,v in ERROR_CODES.items() if v==error_msg] # find key for the given value. It's a dictionary access in reverse. 
    if len(codes_for_msg)!=1:
        raise NotImplementedError("Error message '%s' has no short code defined. Check api.py. %s"%(error_msg,codes_for_msg))
    
    error_code=codes_for_msg[0]

    return error_code



class AccountInputValidation(Validation):
    def is_valid(self, bundle, request=None):
        """Check validity of input parameters."""
        # This runs at an early step in tastypie
        errors = {}
        if not bundle.data:
            return {'__all__': 'Missing parameters'}
        if 'currency' not in bundle.data:
            errors['currency']="Missing currency"
        elif bundle.data['currency'] not in [k for k,v in ALLOWED_CURRENCIES]:
            errors['currency']="Currency not supported"
        return errors

# e.g. http://127.0.0.1:8000/api/account/?format=json
# See scripts/api_client_calls.sh to test this
class AccountResource(ModelResource):
    class Meta:
        queryset = Account.objects.all()
        resource_name = 'accounts'
        authentication = ApiKeyAuthentication() # this requires HTTP header
        authorization = Authorization() # authenticated user can modify everything
        always_return_data = True
        validation = AccountInputValidation()


    def dehydrate(self, bundle):
        """Create the appropriate response, e.g. include an "error" attribute in the response"""

        bundle.data['accountNumber']=bundle.data.pop('number') # rename key
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle

    def error_response(self, request, errors, response_class=None):
        """Wrap the original error handler in order to change the message format according to the requirements"""

        error_code=extract_error_code_from_bundle(errors)

        errors={"error": True, "code": error_code, "message": ERROR_CODES[error_code]}

        # continue normally but with our dict
        res=super(AccountResource,self).error_response(request, errors, response_class)

        return res


class TransactionInputValidation(Validation):
    def is_valid(self, bundle, request=None):
        """This checks basic formats, e.g. the parameters should be present.
        Similar validations are done later in obj_create but they're semantic (e.g. the given accounts must exist)"""
        if not bundle.data:
            return {'__all__': 'Missing parameters'}

        errors = {}

        if 'destAccount' not in bundle.data:
            errors['destAccount']="Missing destination account"
        if 'sourceAccount' not in bundle.data:
            errors['sourceAccount']="Missing source account"

        if 'amount' not in bundle.data:
            errors['amount']="Missing amount"
        elif isinstance(bundle.data['amount'],(float,int)):
            pass
        elif not bundle.data['amount'].replace('.','',1).isdigit():
            errors['amount']="Not a valid number"

        #print("Returning errors:",errors)

        return errors

# also see test programs in scripts/
class TransactionResource(ModelResource):
    class Meta:
        queryset = Transaction.objects.all()
        resource_name = 'transactions'
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        validation = TransactionInputValidation()
        always_return_data = True


    def obj_create(self, bundle, request=None, **kwargs):
        """Extend input data to make it match with model data."""
        #bundle = super(TransactionResource, self).obj_create(bundle, request, user=request.user)

        # Only try to find accounts etc. if the parameters are valid (they exist, valid format, …)
        if self.is_valid(bundle):

            # Validator already checked this, so our usage is safe
            assert 'sourceAccount' in bundle.data
            assert 'destAccount' in bundle.data
            assert 'amount' in bundle.data
    
            # This is what tastypie calls "hydrate": transform text→model. It may get None if we don't find the IDs
            try:
                dest_acc=Account.objects.get(number=bundle.data['destAccount'])
            except Account.DoesNotExist:
                dest_acc=None
            try:
                source_acc=Account.objects.get(number=bundle.data['sourceAccount'])
            except Account.DoesNotExist:
                source_acc=None
            amount=Decimal(bundle.data['amount'])
    
            # Depending on transaction type, fill some data or other. Also, require different data
            if bundle.data['sourceAccount'] is None:
                bundle.obj.op_type='dep'
                # bundle.data['dest_acc']=bundle.data['destAccount']
                if not dest_acc:
                    bundle.errors['destAccount']="Account doesn't exist"
                bundle.obj.dest_acc=dest_acc
                bundle.obj.dest_amount=amount
                bundle.obj.source_acc=None
                bundle.obj.source_amount=None
    
            elif bundle.data['destAccount'] is None:
                bundle.obj.op_type='wd'
                if not source_acc:
                    bundle.errors['sourceAccount']="Account doesn't exist"
                bundle.obj.source_acc=source_acc
                bundle.obj.source_amount=amount
                bundle.obj.dest_acc=None
                bundle.obj.dest_amount=None
    
            elif bundle.data['sourceAccount'] and bundle.data['destAccount']:
                bundle.obj.op_type='tra'
                if not dest_acc:
                    bundle.errors['destAccount']="Account doesn't exist"
                if not source_acc:
                    bundle.errors['sourceAccount']="Account doesn't exist"
                if dest_acc and source_acc and dest_acc==source_acc:
                    bundle.errors['destAccount']="Can't transfer to same account"

                bundle.obj.source_acc=source_acc
                bundle.obj.dest_acc=dest_acc
                # The given amount is always written as source amount. The destination amount, however, can be computed
                bundle.obj.source_amount=amount
                if source_acc and dest_acc and source_acc.currency != dest_acc.currency:
                    #rate=0.5
                    rate=currency_rate(source_acc.currency,dest_acc.currency)
                    rate=Decimal(rate)
                    bundle.obj.dest_amount=amount*rate
                else:
                    # same currency (or nulls)
                    bundle.obj.dest_amount=amount
    
            else:
                raise Exception("check validator")
    
            # extra data
            bundle.obj.date = datetime.datetime.utcnow()
    
            # No need to do hydrate (== transforming key/value to objects) because we did it above
            #bundle = self.full_hydrate(bundle)
        else:
            # if not valid, the save() will not save it
            pass

        # This will check validity before saving and will return error if it finds any problem
        return self.save(bundle)

    def dehydrate(self, bundle):
        """Create the appropriate response, e.g. include an "error" attribute in the response"""
        bundle.data['transactionId']=bundle.data.pop('id') # rename key
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle

    def error_response(self, request, errors, response_class=None):
        """Wrap the original error handler in order to change the message format according to the requirements"""
        error_code=extract_error_code_from_bundle(errors)

        # rewrite the error dict
        errors={"error": True, "code": error_code, "message": ERROR_CODES[error_code]}

        # continue normally but with our dict
        res=super(TransactionResource,self).error_response(request, errors, response_class)

        return res

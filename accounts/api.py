from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.validation import Validation
from accounts.models import Account, Transaction
from accounts.currency import currency_rate
import datetime


ERROR_CODES = {
    'm_par': 'Missing parameters',
    'm_destacc': "Missing destination account",
    'm_srcacc': "Missing source account",
    'm_am': "Missing amount",
    'nf_acc': "Account doesn't exist",
}


# e.g. http://127.0.0.1:8000/api/account/?format=json
# See scripts/api_client_calls.sh to test this
class AccountResource(ModelResource):
    class Meta:
        queryset = Account.objects.all()
        resource_name = 'accounts'
        authentication = ApiKeyAuthentication() # this requires HTTP header
        authorization = Authorization() # authenticated user can modify everything
        always_return_data = True

    def dehydrate(self, bundle):
        """Create the appropriate response, e.g. include an "error" attribute in the response"""
        # TODO add nice error handling (and set error=True). E.g. invalid currency
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle


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
        # TODO parse the amount and check it's a float

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

            # Validator will already checked this:
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
    
            # Depending on transaction type, fill some data or other. Also, require different data
            if bundle.data['sourceAccount'] is None:
                bundle.obj.op_type='dep'
                # bundle.data['dest_acc']=bundle.data['destAccount']
                if not dest_acc:
                    bundle.errors['destAccount']="Account doesn't exist"
                bundle.obj.dest_acc=dest_acc
                bundle.obj.dest_amount=bundle.data['amount']
                #bundle.data['dest_amount']=bundle.data['amount']
                bundle.obj.source_acc=None
                bundle.obj.source_amount=None
    
            elif bundle.data['destAccount'] is None:
                bundle.obj.op_type='wd'
                if not source_acc:
                    bundle.errors['sourceAccount']="Account doesn't exist"
                bundle.obj.source_acc=source_acc
                bundle.obj.source_amount=bundle.data['amount']
                bundle.obj.dest_acc=None
                bundle.obj.dest_amount=None
    
            elif bundle.data['sourceAccount'] and bundle.data['destAccount']:
                bundle.obj.op_type='tra'
                if not dest_acc:
                    bundle.errors['destAccount']="Account doesn't exist"
                if not source_acc:
                    bundle.errors['sourceAccount']="Account doesn't exist"
                # TODO check dest!=source
                bundle.obj.source_acc=source_acc
                bundle.obj.dest_acc=dest_acc
                # The given amount is always written as source amount. The destination amount, however, can be computed
                bundle.obj.source_amount=bundle.data['amount']
                if source_acc and dest_acc and source_acc.currency != dest_acc.currency:
                    #rate=0.5
                    rate=currency_rate(source_acc.currency,dest_acc.currency)
                    bundle.obj.dest_amount=float(bundle.data['amount'])*rate
                else:
                    # same currency (or nulls)
                    bundle.obj.dest_amount=bundle.data['amount']
    
            else:
                raise Exception("check validator")
    
            # extra data
            bundle.obj.date = datetime.datetime.utcnow()
    
            # No need to do hydrate (== transforming key/value to objects) because we did it above
            #bundle = self.full_hydrate(bundle)
        else:
            # if not valid, the save() will not save it
            pass

        return self.save(bundle)

    def dehydrate(self, bundle):
        """Create the appropriate response, e.g. include an "error" attribute in the response"""
        # TODO add more error handling (and set error=True). E.g. invalid amount
        bundle.data['transactionId']=bundle.data.pop('id') # rename key
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle

    def error_response(self, request, errors, response_class=None):
        """Wrap the original error handler in order to change the message format according to the requirements"""
        # Normalize errors. The ones from validator are "transactions: {…}", the ones from obj_create are "{…}"
        if 'transactions' in errors:
            errors=errors['transactions']

        #import ipdb; ipdb.set_trace()

        # the "errors" dict could have many errors but our response format mandates to tell only one. So we take any of them
        error_msg=next(iter(errors.values())) # details: https://stackoverflow.com/questions/3097866/access-an-arbitrary-element-in-a-dictionary-in-python
        codes_for_msg=[k for k,v in ERROR_CODES.items() if v==error_msg] # find key for the given value. It's a dictionary access in reverse. 
        if len(codes_for_msg)!=1:
            raise NotImplementedError("Error message '%s' has no short code defined. Check api.py. %s"%(error_msg,codes_for_msg))
        
        error_code=codes_for_msg[0]

        # rewrite the error dict
        errors={"error": True, "code": error_code, "message": error_msg}

        # continue normally but with our dict
        res=super(TransactionResource,self).error_response(request, errors, response_class)

        return res

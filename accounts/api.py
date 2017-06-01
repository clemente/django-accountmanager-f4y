from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication
from tastypie.validation import Validation
from accounts.models import Account, Transaction
import datetime


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
        # TODO add nice error handling (and set error=True)
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle


class TransactionInputValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'Missing parameters'}

        errors = {}

        if 'destAccount' not in bundle.data:
            errors['destAccount']="Missing destination account"
        if 'sourceAccount' not in bundle.data:
            errors['sourceAccount']="Missing source account"
        if 'amount' not in bundle.data:
            errors['amount']="Missing amount"

        # for key, value in bundle.data.items():
        #     if not isinstance(value, basestring):
        #         continue
        # 
        #     if not 'awesome' in value:
        #         errors[key] = ['NOT ENOUGH AWESOME. NEEDS MORE.']

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

        # Validator already checked this:
        assert 'sourceAccount' in bundle.data
        assert 'destAccount' in bundle.data
        assert 'amount' in bundle.data

        try:
            dest_acc=Account.objects.get(number=bundle.data['destAccount'])
        except Account.DoesNotExist:
            dest_acc=None
        try:
            source_acc=Account.objects.get(number=bundle.data['sourceAccount'])
        except Account.DoesNotExist:
            source_acc=None

        # TODO act on errors


        if bundle.data['sourceAccount'] is None:
            bundle.obj.op_type='dep'
            # bundle.data['dest_acc']=bundle.data['destAccount']
            bundle.obj.dest_acc=dest_acc
            bundle.obj.dest_amount=bundle.data['amount']
            #bundle.data['dest_amount']=bundle.data['amount']
            bundle.obj.source_acc=None
            bundle.obj.source_amount=None
        elif bundle.data['destAccount'] is None:
            bundle.obj.op_type='wd'
            bundle.obj.source_acc=source_acc
            bundle.obj.source_amount=bundle.data['amount']
            bundle.obj.dest_acc=None
            bundle.obj.dest_amount=None
        elif bundle.data['sourceAccount'] and bundle.data['destAccount']:
            bundle.obj.op_type='tra'
            bundle.obj.source_acc=source_acc
            bundle.obj.dest_acc=dest_acc
            # FIXME detect intercurrency transfers and store different amounts
            bundle.obj.source_amount=bundle.data['amount']
            bundle.obj.dest_amount=bundle.data['amount']
        else:
            raise Exception("check validator")

        # extra data
        bundle.obj.date = datetime.datetime.utcnow()

        # No need to do hydrate (== transforming key/value to objects) because we did it above
        #bundle = self.full_hydrate(bundle)

        return self.save(bundle)

    def dehydrate(self, bundle):
        """Create the appropriate response, e.g. include an "error" attribute in the response"""
        # TODO add nice error handling (and set error=True)
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle



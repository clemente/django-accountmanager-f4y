from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication
from accounts.models import Account


# e.g. http://127.0.0.1:8000/api/account/?format=json
# See scripts/api_client_calls.sh to test this
class AccountResource(ModelResource):
    class Meta:
        queryset = Account.objects.all()
        resource_name = 'account'
        authentication = ApiKeyAuthentication() # this requires HTTP header
        authorization = Authorization() # authenticated user can modify everything
        always_return_data = True

    def dehydrate(self, bundle):
        """Create the appropriate response, e.g. include an "error" attribute in the response"""
        # TODO add nice error handling (and set error=True)
        bundle.data['request_ip'] = bundle.request.META.get('REMOTE_ADDR')
        orig_data=dict(bundle.data)
        bundle.data={'error':False, 'data':orig_data}
        return bundle

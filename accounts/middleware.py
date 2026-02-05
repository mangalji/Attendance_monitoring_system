from django.utils.deprecation import MiddlewareMixin

class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if request.user.is_authenticated:
            request.session.set_expiry(30000)# for 500 minutes == 30000 seconds
        return None

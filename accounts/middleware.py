from django.utils.deprecation import MiddlewareMixin

class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if request.user.is_authenticated:
            request.session.set_expiry(300)# for 5 minutes == 300 seconds
        return None

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import ActiveSession

class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self,request):
        if request.user.is_authenticated:
            request.session.set_expiry(30000)# for 500 minutes == 30000 seconds
        return None


class SingleSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return None

        session_key = request.session.session_key
        if not session_key:
            return None

        active_session = getattr(request.user, 'active_session', None)
        if active_session and active_session.session_key != session_key:
            logout(request)
            return redirect('login')

        return None

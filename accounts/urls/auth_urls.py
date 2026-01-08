from django.urls import path
from accounts.views.auth_views import login_view, logout_view, post_login_redirect

urlpatterns = [
    path("login/",login_view, name="login"),
    path("logout/",logout_view,name="logout"),
    path("redirect/",post_login_redirect,name="post_login_redirect"),
]

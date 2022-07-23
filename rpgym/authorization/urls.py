from django.urls import path, include
from authorization.views import Logout, GoogleLogin, GoogleLoginApi, TokenObtainPair, TokenRefresh, RefreshCookieToken

app_name = "auth"

token_patterns = [
    path('', TokenObtainPair.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefresh.as_view(), name='token_refresh'),
    path('refresh_cookie/', RefreshCookieToken.as_view(), name='token_cookie_refresh'),
]

urlpatterns = [
    path("token/", include(token_patterns)),
    path("login/", GoogleLogin.as_view()),
    path("logout/", Logout.as_view()),
    path("google_login/", GoogleLoginApi.as_view(), name="login_with_google"),
]

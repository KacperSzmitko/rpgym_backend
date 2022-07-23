from django.http import HttpRequest
from isort import code
from rest_framework.views import APIView
from rest_framework import serializers
from django.shortcuts import redirect
from urllib.parse import urlencode
from requests.models import PreparedRequest
from django.conf import settings
from django.urls import reverse
from authorization.services import google_get_access_token, google_get_user_info
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def set_tokens_cookies(response: Response, access_expires: int = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(), refresh_expires: int = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(), * args, **kwargs):
    """Store tokens in cookies to perist user login

    Args:
        response (Response): Prepared response from view
        access_expires (int, optional): How long to store access token in cookies in seconds. Defaults to settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].seconds.
        refresh_expires (int, optional): How long to store refresh token in cookies in seconds. Defaults to settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].seconds.
    """
    response.set_cookie(
        settings.SIMPLE_JWT['AUTH_COOKIE'], response.data['access'], max_age=access_expires, expires=access_expires, httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'], samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
    response.set_cookie(
        settings.SIMPLE_JWT['REFRESH_COOKIE'], response.data['refresh'], max_age=refresh_expires, expires=refresh_expires, httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'], samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
    return response


class TokenObtainPair(TokenObtainPairView):
    def post(self, request: Request, * args, **kwargs):
        # print(request.COOKIES)
        # TODO Cookies by statement
        response = super().post(request, *args, **kwargs)
        return set_tokens_cookies(response)


class TokenRefresh(TokenRefreshView):
    def post(self, request: Request, * args, **kwargs):
        # TODO Cookies by statement
        response = super().post(request, *args, **kwargs)
        return set_tokens_cookies(response)


class Logout(APIView):
    def post(self, request: Request, * args, **kwargs):
        response = Response(status=200)
        response.delete_cookie("access", samesite="Lax")
        response.delete_cookie("refresh", samesite="Lax")
        return response




class RefreshCookieToken(APIView):
    def get(self, request: Request, * args, **kwargs):
        refresh = request.COOKIES.get("refresh", "")
        if refresh:
            token = RefreshToken(refresh)
            user = User.objects.get(pk=token['user_id'])
            refresh = RefreshToken.for_user(user)
            response = Response(data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
            return set_tokens_cookies(response)
        return Response(status=401)



class GoogleLogin(APIView):
    def get(self, request, format=None):
        domain = settings.BASE_URL
        api_uri = reverse('api:v1:auth:login_with_google')
        redirect_uri = f'{domain}{api_uri}'
        req = PreparedRequest()
        scope = ' '.join([
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ])
        url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {'response_type': "code",
                  "prompt": "select_account", "access_type": "offline", "redirect_uri": redirect_uri, "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID, "scope": scope}
        req.prepare_url(url, params)
        return redirect(req.url)


class GoogleLoginApi(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        # TODO Cookies by statement
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = f'user'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        domain = settings.BASE_URL
        api_uri = reverse('api:v1:auth:login_with_google')
        redirect_uri = f'{domain}{api_uri}'

        access_token = google_get_access_token(
            code=code, redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)

        profile_data = {
            'email': user_data['email'],
            'first_name': user_data.get('givenName', ''),
            'last_name': user_data.get('familyName', ''),
        }
        user, _ = User.objects.get_or_create(**profile_data)
        refresh = RefreshToken.for_user(user)
        response = Response(data={
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
        return set_tokens_cookies(response)

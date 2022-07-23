from django.urls import path, include

app_name = "api"

v1_patterns = [path("auth/", include(("authorization.urls", "authorization"))),
               path("users/", include(("users.urls", "users"))),
               path("app/", include("app.urls", "app"))]

urlpatterns = [
    path('v1/', include((v1_patterns, 'v1'))),
]

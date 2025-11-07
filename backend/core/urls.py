from django.contrib import admin
from django.urls import path, include
from users.views import UserDetailsView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/courses/", include("courses.urls"))
]
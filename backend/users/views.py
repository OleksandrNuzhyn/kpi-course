from dj_rest_auth.views import UserDetailsView as DefaultUserDetailsView
from .serializers import CustomUserDetailsSerializer


class UserDetailsView(DefaultUserDetailsView):
    serializer_class = CustomUserDetailsSerializer
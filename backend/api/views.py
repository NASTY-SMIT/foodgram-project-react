from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import AllowAny
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(DjoserUserViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        else:
            return UserSerializer

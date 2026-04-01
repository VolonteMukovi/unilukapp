from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.serializers import UserProfileSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = User.objects.prefetch_related("filieres__domaine__institution").get(
            pk=self.user.pk
        )
        data["user"] = UserProfileSerializer(user, context=self.context).data
        return data

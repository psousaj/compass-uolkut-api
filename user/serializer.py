from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import CustomUser, Profile


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # fields = "__all__"
        fields = [
            "id",
            "email",
            "username",
            "is_staff",
            "last_login",
        ]


class CustomUserSerializerToProfile(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializerToProfile(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "name",
            "birth",
            "profession",
            "relationship",
            "country",
            "city",
            "user",
        ]


class MyTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        profile = ProfileSerializer(instance=user.user_profile)
        token = super().get_token(user)

        # Add custom claims
        token["profile"] = profile

        return token

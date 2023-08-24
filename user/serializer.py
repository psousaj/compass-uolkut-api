from rest_framework import serializers

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

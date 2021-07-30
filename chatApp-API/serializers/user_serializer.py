from rest_framework import serializers
from userApp.models import User


class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username',
                  'email')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username',
                  'email')

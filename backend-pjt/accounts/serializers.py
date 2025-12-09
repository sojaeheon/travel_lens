from rest_framework import serializers
from accounts.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("email", "name", "password")  # name 추가

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data["name"],     # name 저장
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user
    
    def validate_name(self, value):
        if User.objects.filter(name=value).exists():
            raise serializers.ValidationError("이미 사용 중인 닉네임입니다.")
        return value

class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.name     # name도 JWT payload에 포함 가능
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "name": self.user.name,  # 응답에 name 포함
        }

        return data

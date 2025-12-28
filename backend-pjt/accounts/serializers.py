from rest_framework import serializers
from accounts.models import User
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

##################################
# 사용자 비밀번호 변경 Serializers
##################################
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("기존 비밀번호가 올바르지 않습니다.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "새 비밀번호가 일치하지 않습니다."}
            )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

########################
# 회원가입 Serializer
########################
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

#############################
# 로그인 Serailizer
#############################
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

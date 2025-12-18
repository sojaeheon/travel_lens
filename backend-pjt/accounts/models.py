from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser,   # 비밀번호, 로그인 관련 기능(비밀번호, 해시, last_login 필드 등)을 제공해주는 추상 User베이스 클래스
  PermissionsMixin,   # is_superuser, groups, user_permissions 같은 권한 시스템 관련 필드 + 메서드를 제공. 장고의 권한 시스템(request.user.is_authenticated,is_superuser) 사용가능
  BaseUserManager     # create_user(), create_superuser() 같은 User 생성 로직을 커스터마이징 하기 위한 Manager 베이스 클래스
)

###########################################################
# User 생성/슈퍼유저 생성 시, 비밀번호를 안전하게 해시하고,
# 이메일 필수로 받도록 제어하는 매니저
###########################################################
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,unique=True)
    email = models.EmailField(unique=True)
    # 이미 AbstractBaseUser에 password에 대한 필드가 존재, 중복 방지로 삭제
    # password = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "User"

    def __str__(self):
        return self.email
# Swagger관련 라이브러리
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# REST API 관련 라이브러리
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# 필요한 serializer 임포트
from accounts.serializers import RegisterSerializer, LoginSerializer, ChangePasswordSerializer
# JWT 기반 인증방식 로그인 관련 라이브러리
from rest_framework_simplejwt.views import TokenObtainPairView
# 인증 라이브러리
from rest_framework.permissions import IsAuthenticated

# ======================================
#   회원가입 API
# ======================================
class RegisterAPIView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_description="회원가입 API",
        responses={201: "회원가입 성공", 400: "잘못된 요청"}
    )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "회원가입이 완료되었습니다."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ======================================
#   로그인 API (JWT 발급)
# ======================================
class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    

# ======================================
#   비밀번호 변경 API
# ======================================
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        operation_description="비밀번호 변경 API (로그인 필요)",
        responses={
            200: "비밀번호 변경 성공",
            400: "잘못된 요청",
            401: "인증 실패"
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "비밀번호가 성공적으로 변경되었습니다."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

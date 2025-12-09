from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


# ======================================
#   회원가입 API
# ======================================
class RegisterAPIView(APIView):

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

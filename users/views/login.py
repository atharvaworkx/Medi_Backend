from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from users.models import Users
import logging

logger = logging.getLogger(__name__)


class CustomTokenPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, data):
        try:
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                raise serializers.ValidationError(_("Email and password are required"))
            
            user = Users.objects.get(email=email)
            
            if not user.isVerified:
                raise serializers.ValidationError(_("User account is not verified. Please check your email."))
            
            if not user.check_password(password):
                raise serializers.ValidationError(_("Invalid email or password"))

            token = RefreshToken.for_user(user)
            res_data = {
                'refresh': str(token),
                'access': str(token.access_token),
                'userId': str(user.id),
                'firstName': user.firstName or '',
                'lastName': user.lastName or '',
                'email': user.email,
                'phone': user.phone or '',
                'age': 0,
                'gender': '',
            }
            return res_data
        except Users.DoesNotExist:
            raise serializers.ValidationError(_("Invalid email or password"))
        except Exception as e:
            logger.error(f"Login validation error: {str(e)}", exc_info=True)
            raise serializers.ValidationError(_("An error occurred during login"))


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Login view error: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminLoginView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = Users.objects.get(email=request.data.get('email'))
            if not user.is_staff and not user.is_superuser:
                return Response(
                    {"detail": "Only admins can login here"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Admin login error: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}", exc_info=True)
            return Response(
                {"detail": "Logout failed"},
                status=status.HTTP_400_BAD_REQUEST
            )

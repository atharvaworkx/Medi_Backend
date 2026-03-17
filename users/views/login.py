from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from users.models import Users


class CustomTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, data):
        try:
            user = Users.objects.get(email=data['email'])
            if not user.isVerified:
                raise serializers.ValidationError(_(("User with email %(email)s is not verified. Check your email or contact support.") % {'email': data['email']}))
            
            # Simple validation check
            if not user.check_password(data['password']):
                 raise serializers.ValidationError(_("Invalid password"))

            # Include profile data
            from profiles.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(userId=user)
            
            token = RefreshToken.for_user(user)
            res_data = dict()
            res_data['refresh'] = str(token)
            res_data['access'] = str(token.access_token)
            res_data['userId'] = str(user.id)
            res_data['firstName'] = user.firstName
            res_data['lastName'] = user.lastName
            res_data['email'] = user.email
            res_data['phone'] = user.phone or ""
            res_data['age'] = profile.age
            res_data['gender'] = profile.gender
            return res_data
        except Users.DoesNotExist:
            raise serializers.ValidationError(_(("User with email %(email)s does not exist") % {'email': data['email']}))


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer
    permission_classes = [AllowAny]


class AdminLoginView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        user = Users.objects.get(email=request.data['email'])
        if not user.is_staff and not user.is_superuser:
            return Response({"detail": "Only admins can login here"}, status=status.HTTP_403_FORBIDDEN)
            
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

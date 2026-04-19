from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSignupSerializer
import logging

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    Patient self-registration endpoint.
    POST /api/v1/register/
    Body: { email, firstName, lastName, phone, password, passwordConfirm }
    Returns: { access, refresh, userId, firstName, lastName, email }
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        try:
            serializer = UserSignupSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token = RefreshToken.for_user(user)
                return Response({
                    'access': str(token.access_token),
                    'refresh': str(token),
                    'userId': str(user.id),
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'email': user.email,
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Register error: {str(e)}", exc_info=True)
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

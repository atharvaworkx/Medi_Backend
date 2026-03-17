# Standard Imports

# 3rd party libraries imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

# app imports
from users.models import Users, UsersDevices
from users.serializers import (
    UsersSerializer,
    UsersDevicesSerializer,
    UploadProfilePictureSerializer,
    UpdateAdminStatusSerializer
)
from users.permissions import UsersPermission
from users.filters import UsersFilter, UsersDevicesFilter
from atomicloops.viewsets import AtomicViewSet

try:
    from utils.aws_script import upload_image
except Exception:
    upload_image = None


# Users View
class UsersView(AtomicViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated, UsersPermission]
    filterset_class = UsersFilter
    search_fields = [
        'firstName',
        'lastName',
        'email',
    ]
    ordering_fields = (
        'createdAt',
        'updatedAt',
    )

    # This will be used as the default ordering
    ordering = ('-createdAt',)

    def create(self, request, *args, **kwargs):
        return Response("Method Not Allowed", status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['post'], url_path='update-admin-user')
    def update_admin_user(self, request, *args, **kwargs):
        try:
            serializer_class = UpdateAdminStatusSerializer
            if not request.user.is_superuser:
                return Response("Unauthorized user", status=status.HTTP_403_FORBIDDEN)
            if not isinstance(request.data, list):
                raise ValidationError('Request body must be a list')
            if request.data == []:
                raise ValidationError('Empty data not permitted')
            if len(request.data) > 100:
                raise ValidationError('Number of list elements must not be greater than 100')
            ids = self.validate_ids(request.data)
            instances = Users.objects.filter(id__in=ids)
            fields = [f.name for f in Users._meta.concrete_fields]
            fields.remove('id')
            _ = Users.objects.bulk_update(instances, fields)
            serializer = serializer_class(instances, many=True, partial=True, context={'request': self.request, 'view': self})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        tokens = OutstandingToken.objects.filter(user_id=instance.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='upload-profile')
    def upload_profile(self, request, *args, **kwargs):
        image = request.FILES.get('file', None)
        if not image:
            return Response("Image not found", status=status.HTTP_400_BAD_REQUEST)
        if not upload_image:
            return Response("Image upload not configured", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        image_url = upload_image(image, folder="profiles")
        data = {
            'profilePicture': image_url
        }
        serialized_data = UploadProfilePictureSerializer(instance=request.user, data=data, partial=True)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data, status=status.HTTP_200_OK)
        return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)


# users devices views
class UsersDevicesView(ModelViewSet):
    queryset = UsersDevices.objects.all()
    serializer_class = UsersDevicesSerializer
    filterset_class = UsersDevicesFilter
    search_fields = [
        'userId__firstName',
        'userId__lastName',
        'userId__email',
    ]
    ordering_fields = (
        'createdAt',
        'updatedAt',
    )

    # This will be used as the default ordering
    ordering = ('-createdAt',)


# Upload Image API
class UploadImageView(APIView):
    serializer_class = UsersSerializer

    def post(self, request, *args, **kwargs):
        file = request.FILES['file'] if 'file' in request.FILES else None

        if file is None:
            return Response({"message": "File Not Provided"}, status.HTTP_400_BAD_REQUEST)

        url = upload_image(file, folder="profiles")
        if url is None:
            return Response({"message": "File not Uploaded"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "OK", "imageUrl": url}, status.HTTP_201_CREATED)


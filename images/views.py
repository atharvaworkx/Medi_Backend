import logging

from django.conf import settings
from PIL import Image
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from images.models import HealthImage
from images.serializers import HealthImageSerializer

logger = logging.getLogger(__name__)


class HealthImageViewSet(viewsets.ModelViewSet):
    serializer_class = HealthImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HealthImage.objects.filter(userId=self.request.user)

    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload(self, request):
        """Store an image directly in PostgreSQL."""
        image_type = request.data.get('imageType')
        image_file = request.FILES.get('file')
        allowed_types = {'iris', 'tongue', 'hair', 'skin'}
        allowed_content_types = {'image/jpeg', 'image/png'}
        max_size = getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024)

        if image_type not in allowed_types:
            return Response(
                {'status': 'error', 'message': 'Invalid imageType'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not image_file:
            return Response(
                {'status': 'error', 'message': 'A file field is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if image_file.content_type not in allowed_content_types:
            return Response(
                {'status': 'error', 'message': 'Only JPEG and PNG images are supported'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if image_file.size <= 0 or image_file.size > max_size:
            return Response(
                {'status': 'error', 'message': 'Image exceeds the allowed size'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_bytes = image_file.read()
        try:
            image_file.seek(0)
            with Image.open(image_file) as image:
                image.verify()
        except Exception:
            return Response(
                {'status': 'error', 'message': 'Invalid image file'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image = HealthImage.objects.create(
            userId=request.user,
            imageType=image_type,
            imageUrl=None,
            fileSize=len(image_bytes),
            imageData=image_bytes,
            contentType=image_file.content_type,
            processingStatus='pending',
        )
        return Response(
            {
                'status': 'success',
                'imageId': str(image.id),
                'imageType': image.imageType,
                'fileSize': image.fileSize,
                'contentType': image.contentType,
                'processingStatus': image.processingStatus,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        image_type = request.query_params.get('type')
        if image_type:
            images = self.get_queryset().filter(imageType=image_type)
            serializer = self.get_serializer(images, many=True, context={'request': request})
            return Response({'status': 'success', 'images': serializer.data})
        return Response(
            {'status': 'error', 'message': 'Type parameter required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

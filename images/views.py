import uuid
import logging
from pathlib import PurePath
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from images.models import HealthImage
from images.serializers import HealthImageSerializer, ImageUploadInitSerializer

logger = logging.getLogger(__name__)


class HealthImageViewSet(viewsets.ModelViewSet):
    serializer_class = HealthImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HealthImage.objects.filter(userId=self.request.user)

    @action(detail=False, methods=['post'])
    def request_upload_url(self, request):
        """Request pre-signed S3 upload URL"""
        serializer = ImageUploadInitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'status': 'error', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        if not bucket:
            return Response(
                {'status': 'error', 'message': 'Image storage is not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        image_type = serializer.validated_data['imageType']
        file_name = PurePath(serializer.validated_data['fileName']).name
        content_type = serializer.validated_data['contentType']
        file_size = serializer.validated_data['fileSize']
        max_image_size = getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024)
        if file_size <= 0 or file_size > max_image_size:
            return Response(
                {'status': 'error', 'message': 'Image exceeds the allowed size'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = f"health-images/{request.user.id}/{uuid.uuid4()}-{file_name}"
        try:
            client = boto3.client('s3', region_name=region)
            upload_url = client.generate_presigned_url(
                'put_object',
                Params={'Bucket': bucket, 'Key': key, 'ContentType': content_type},
                ExpiresIn=900,
            )
        except (BotoCoreError, ClientError):
            logger.exception("Could not create S3 upload URL")
            return Response(
                {'status': 'error', 'message': 'Could not prepare image upload'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        image_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        image = HealthImage.objects.create(
            userId=request.user,
            imageType=image_type,
            imageUrl=image_url,
            s3Key=key,
            fileSize=file_size,
            processingStatus='pending',
        )
        return Response({
            'status': 'success',
            'imageId': str(image.id),
            'uploadUrl': upload_url,
            'imageUrl': image_url,
            'expiresIn': 900,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get images by type"""
        image_type = request.query_params.get('type')
        if image_type:
            images = self.get_queryset().filter(imageType=image_type)
            serializer = self.get_serializer(images, many=True, context={'request': request})
            return Response({
                'status': 'success',
                'images': serializer.data
            })
        return Response({'status': 'error', 'message': 'Type parameter required'}, status=status.HTTP_400_BAD_REQUEST)

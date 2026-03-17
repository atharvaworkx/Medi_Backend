from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from images.models import HealthImage
from images.serializers import HealthImageSerializer, ImageUploadInitSerializer


class HealthImageViewSet(viewsets.ModelViewSet):
    serializer_class = HealthImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HealthImage.objects.filter(userId=self.request.user)

    @action(detail=False, methods=['post'])
    def request_upload_url(self, request):
        """Request pre-signed S3 upload URL"""
        serializer = ImageUploadInitSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: Integrate with S3 service
            # For now, create image record with placeholder
            image = HealthImage.objects.create(
                userId=request.user,
                imageType=serializer.validated_data['imageType'],
                imageUrl='',  # Will be filled by S3
                fileSize=serializer.validated_data['fileSize'],
                processingStatus='pending'
            )

            return Response({
                'status': 'success',
                'imageId': str(image.id),
                'uploadUrl': 'https://s3.example.com/upload',  # Placeholder
                'message': 'S3 integration required for actual URL'
            }, status=status.HTTP_200_OK)

        return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

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

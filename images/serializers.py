from rest_framework import serializers
from atomicloops.serializers import AtomicSerializer
from images.models import HealthImage


class HealthImageSerializer(AtomicSerializer):
    class Meta:
        model = HealthImage
        fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'imageType', 'imageUrl', 's3Key',
            'fileSize', 'uploadedAt', 'aiProcessed', 'aiResults', 'processingStatus'
        ]
        get_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'imageType', 'imageUrl', 's3Key',
            'fileSize', 'uploadedAt', 'aiProcessed', 'aiResults', 'processingStatus'
        ]
        list_fields = [
            'id', 'createdAt', 'updatedAt', 'imageType', 'imageUrl', 'aiProcessed', 'processingStatus'
        ]
        read_only_fields = ['id', 'userId', 'imageUrl', 's3Key', 'uploadedAt', 'aiProcessed', 'aiResults', 'createdAt', 'updatedAt']


class ImageUploadInitSerializer(serializers.Serializer):
    imageType = serializers.ChoiceField(choices=['iris', 'tongue', 'hair', 'skin'])
    fileName = serializers.CharField(max_length=255)
    fileSize = serializers.IntegerField()
    contentType = serializers.CharField(max_length=50)

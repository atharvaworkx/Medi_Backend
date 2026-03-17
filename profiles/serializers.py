from rest_framework import serializers
from atomicloops.serializers import AtomicSerializer
from profiles.models import UserProfile


class UserProfileSerializer(AtomicSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'fullName', 'age',
            'dateOfBirth', 'gender', 'location', 'heightCm', 'weightKg', 'bloodType', 'bio'
        ]
        get_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'fullName', 'age',
            'dateOfBirth', 'gender', 'location', 'heightCm', 'weightKg', 'bloodType', 'bio'
        ]
        list_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'fullName', 'gender', 'location'
        ]
        read_only_fields = ['id', 'userId', 'createdAt', 'updatedAt']

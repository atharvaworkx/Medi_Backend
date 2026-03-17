from rest_framework import serializers
from atomicloops.serializers import AtomicSerializer
from medical.models import MedicalHistory, MedicalHistoryVersion


class MedicalHistorySerializer(AtomicSerializer):
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'existingConditions', 'ongoingTreatments',
            'allergies', 'familyMedicalHistory', 'medications', 'lifestyleNotes', 'version', 'isActive'
        ]
        get_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'existingConditions', 'ongoingTreatments',
            'allergies', 'familyMedicalHistory', 'medications', 'lifestyleNotes', 'version', 'isActive'
        ]
        list_fields = [
            'id', 'createdAt', 'updatedAt', 'userId', 'version', 'isActive'
        ]
        read_only_fields = ['id', 'userId', 'version', 'createdAt', 'updatedAt']


class MedicalHistoryVersionSerializer(AtomicSerializer):
    class Meta:
        model = MedicalHistoryVersion
        fields = ['id', 'createdAt', 'updatedAt', 'userId', 'versionData', 'versionNumber']
        get_fields = ['id', 'createdAt', 'updatedAt', 'userId', 'versionData', 'versionNumber']
        list_fields = ['id', 'createdAt', 'updatedAt', 'versionNumber']
        read_only_fields = ['id', 'userId', 'createdAt', 'updatedAt']

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from medical.models import MedicalHistory, MedicalHistoryVersion
from medical.serializers import MedicalHistorySerializer, MedicalHistoryVersionSerializer


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MedicalHistory.objects.filter(userId=self.request.user, isActive=True)

    @action(detail=False, methods=['get', 'post', 'patch'])
    def my_medical_history(self, request):
        medical_history, created = MedicalHistory.objects.get_or_create(userId=request.user)

        if request.method == 'GET':
            serializer = MedicalHistorySerializer(medical_history, context={'request': request})
            return Response(serializer.data)

        try:
            if request.method in ['POST', 'PATCH']:
                # Archive previous version
                if not created:
                    version_data = {
                        'existingConditions': medical_history.existingConditions or [],
                        'ongoingTreatments': medical_history.ongoingTreatments or [],
                        'allergies': medical_history.allergies or [],
                        'familyMedicalHistory': medical_history.familyMedicalHistory or {},
                        'medications': medical_history.medications or [],
                        'lifestyleNotes': medical_history.lifestyleNotes,
                    }
                    MedicalHistoryVersion.objects.create(
                        userId=request.user,
                        versionData=version_data,
                        versionNumber=medical_history.version
                    )

                serializer = MedicalHistorySerializer(
                    medical_history,
                    data=request.data,
                    partial=True,
                    context={'request': request}
                )
                if serializer.is_valid():
                    # Update version
                    medical_history.version += 1
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def history_versions(self, request):
        versions = MedicalHistoryVersion.objects.filter(userId=request.user)
        serializer = MedicalHistoryVersionSerializer(versions, many=True, context={'request': request})
        return Response({
            'status': 'success',
            'versions': serializer.data
        })

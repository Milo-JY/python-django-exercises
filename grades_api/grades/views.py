from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Grade
from .serializers import GradeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
import statistics

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        grades = self.get_queryset().values_list('score', flat=True)
        if grades:
            return Response({
                'mean': statistics.mean(grades),
                'median': statistics.median(grades),
                'mode': statistics.mode(grades),
            })
        return Response({'error': 'No grades available'})
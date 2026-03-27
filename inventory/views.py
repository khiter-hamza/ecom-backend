from rest_framework import viewsets, permissions
from .models import StockMovement
from .serializers import StockMovementSerializer

class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAdminUser]

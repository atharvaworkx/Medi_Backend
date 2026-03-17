from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, Subscription
from orders.serializers import (
    OrderSerializer, CheckoutSerializer, SubscriptionSerializer,
    SubscriptionCreateSerializer
)
from orders.services.order_service import OrderService
from medicines.models import Medicine
from datetime import datetime, timedelta


class OrderViewSet(viewsets.ModelViewSet):
    """Manage medicine orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter orders by patient."""
        return Order.objects.filter(patient=self.request.user).select_related('patient').prefetch_related('items')
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Checkout and create order.
        POST /api/orders/checkout/
        """
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order, response = OrderService.checkout(
            request.user,
            serializer.validated_data['items']
        )
        
        if order:
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel order.
        POST /api/orders/{id}/cancel/
        """
        order = self.get_object()
        
        # Verify ownership
        if order.patient != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = OrderService.cancel_order(order)
        
        return Response(
            response,
            status=status.HTTP_200_OK if response['status'] == 'success' else status.HTTP_400_BAD_REQUEST
        )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Manage medicine subscriptions."""
    
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter subscriptions by patient."""
        return Subscription.objects.filter(patient=self.request.user).select_related('patient', 'medicine')
    
    @action(detail=False, methods=['post'])
    def create_subscription(self, request):
        """
        Create medicine subscription.
        POST /api/subscriptions/create_subscription/
        """
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        medicine = Medicine.objects.get(id=serializer.validated_data['medicine_id'])
        
        # Check if subscription already exists
        existing = Subscription.objects.filter(
            patient=request.user,
            medicine=medicine
        ).first()
        
        if existing:
            return Response(
                {'error': 'Subscription already exists for this medicine'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate next delivery date
        next_delivery = datetime.now().date() + timedelta(days=30)
        
        subscription = Subscription.objects.create(
            patient=request.user,
            medicine=medicine,
            quantity=serializer.validated_data.get('quantity', 1),
            interval=serializer.validated_data['interval'],
            next_delivery_date=next_delivery,
            is_active=True
        )
        
        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel_subscription(self, request, pk=None):
        """
        Cancel subscription.
        POST /api/subscriptions/{id}/cancel_subscription/
        """
        subscription = self.get_object()
        
        # Verify ownership
        if subscription.patient != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription.is_active = False
        subscription.save()
        
        return Response(
            {'status': 'success', 'message': 'Subscription cancelled'},
            status=status.HTTP_200_OK
        )

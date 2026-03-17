from django.urls import path
from rest_framework.routers import DefaultRouter
from orders.views import OrderViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = router.urls

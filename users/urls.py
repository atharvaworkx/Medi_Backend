# Imports
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views.users import UsersView, UsersDevicesView
from .views.update_password import UpdatePasswordView
from .views.login import LoginView
from .views.login import AdminLoginView
from .views.logout import LogoutView, LogoutAllView
from .views.register import RegisterView
from .views.reset_password import (
    reset_password_validate_token,
    reset_password_confirm,
    reset_password_request_token
)
from .views.admin_reset_password import (
    admin_reset_password_validate_token,
    admin_reset_password_confirm,
    admin_reset_password_request_token
)
from .views import AuthViewSet


router = DefaultRouter()
router.register('users', UsersView, basename='users')
router.register('users-devices', UsersDevicesView, basename='users-devices')
router.register('auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token-obtain-pair'),
    path('admin-login/', AdminLoginView.as_view(), name='token-obtain-pair-admin'),
    path('update-password/<uuid:pk>/', UpdatePasswordView.as_view(), name='auth_change_password'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('reset-password/validate-token/', reset_password_validate_token, name='reset-password-validate'),
    path('reset-password/confirm/', reset_password_confirm, name='reset-password-confirm'),
    path('reset-password/request/', reset_password_request_token, name='reset-password-request'),
    path('admin-reset-password/validate-token/', admin_reset_password_validate_token, name='admin-reset-password-validate'),
    path('admin-reset-password/confirm/', admin_reset_password_confirm, name='admin-reset-password-confirm'),
    path('admin-reset-password/request/', admin_reset_password_request_token, name='admin-reset-password-request'),
]

urlpatterns += router.urls

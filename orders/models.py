from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import Users
from medicines.models import Medicine
from datetime import datetime, timedelta


class Order(models.Model):
    """Medicine orders."""
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )
    
    patient = models.ForeignKey(
        Users,
        verbose_name=_('Patient'),
        on_delete=models.CASCADE,
        related_name='orders',
        db_column='patient_id'
    )
    total_amount = models.DecimalField(
        verbose_name=_('Total Amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='total_amount'
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_column='status'
    )
    payment_status = models.CharField(
        verbose_name=_('Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_column='payment_status'
    )
    notes = models.TextField(
        verbose_name=_('Order Notes'),
        null=True,
        db_column='notes'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'orders'
        verbose_name_plural = 'Orders'
        managed = True
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} - {self.patient.firstName}"


class OrderItem(models.Model):
    """Individual items in an order."""
    
    order = models.ForeignKey(
        Order,
        verbose_name=_('Order'),
        on_delete=models.CASCADE,
        related_name='items',
        db_column='order_id'
    )
    medicine = models.ForeignKey(
        Medicine,
        verbose_name=_('Medicine'),
        on_delete=models.SET_NULL,
        null=True,
        db_column='medicine_id'
    )
    quantity = models.IntegerField(
        verbose_name=_('Quantity'),
        validators=[MinValueValidator(1)],
        db_column='quantity'
    )
    price_at_purchase = models.DecimalField(
        verbose_name=_('Price at Purchase'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='price_at_purchase'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        db_column='created_at'
    )
    
    class Meta:
        db_table = 'order_items'
        verbose_name_plural = 'Order Items'
        managed = True
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['medicine']),
        ]
    
    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"


class Subscription(models.Model):
    """Medicine subscription for recurring deliveries."""
    
    INTERVAL_CHOICES = (
        ('monthly', _('Monthly')),
        ('quarterly', _('Quarterly')),
        ('biannual', _('Biannual')),
        ('annual', _('Annual')),
    )
    
    patient = models.ForeignKey(
        Users,
        verbose_name=_('Patient'),
        on_delete=models.CASCADE,
        related_name='subscriptions',
        db_column='patient_id'
    )
    medicine = models.ForeignKey(
        Medicine,
        verbose_name=_('Medicine'),
        on_delete=models.CASCADE,
        related_name='subscriptions',
        db_column='medicine_id'
    )
    quantity = models.IntegerField(
        verbose_name=_('Quantity per Delivery'),
        validators=[MinValueValidator(1)],
        db_column='quantity',
        default=1
    )
    interval = models.CharField(
        verbose_name=_('Delivery Interval'),
        max_length=20,
        choices=INTERVAL_CHOICES,
        db_column='interval'
    )
    next_delivery_date = models.DateField(
        verbose_name=_('Next Delivery Date'),
        db_column='next_delivery_date'
    )
    is_active = models.BooleanField(
        verbose_name=_('Is Active'),
        default=True,
        db_column='is_active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        db_column='updated_at'
    )
    
    class Meta:
        db_table = 'subscriptions'
        verbose_name_plural = 'Subscriptions'
        managed = True
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['medicine']),
            models.Index(fields=['is_active']),
            models.Index(fields=['next_delivery_date']),
        ]
        unique_together = ('patient', 'medicine')
    
    def __str__(self):
        return f"{self.patient.firstName} - {self.medicine.name} ({self.interval})"
    
    def get_next_delivery(self) -> datetime:
        """Calculate next delivery date based on interval."""
        interval_map = {
            'monthly': 30,
            'quarterly': 90,
            'biannual': 180,
            'annual': 365,
        }
        days = interval_map.get(self.interval, 30)
        return self.next_delivery_date + timedelta(days=days)

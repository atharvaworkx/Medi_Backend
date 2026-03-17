from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Medicine(models.Model):
    """Ayurvedic medicine catalog."""
    
    CATEGORY_CHOICES = (
        ('ayurvedic', _('Ayurvedic')),
        ('herbal', _('Herbal')),
        ('allopathic', _('Allopathic')),
    )
    
    DOSHA_AFFINITY = (
        ('vata', _('Vata')),
        ('pitta', _('Pitta')),
        ('kapha', _('Kapha')),
        ('general', _('General')),
    )
    
    name = models.CharField(
        verbose_name=_('Medicine Name'),
        max_length=200,
        unique=True,
        db_column='name'
    )
    category = models.CharField(
        verbose_name=_('Category'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_column='category'
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
        db_column='description'
    )
    dosage_info = models.TextField(
        verbose_name=_('Dosage Information'),
        null=True,
        db_column='dosage_info'
    )
    dosha_affinity = models.CharField(
        verbose_name=_('Dosha Affinity'),
        max_length=20,
        choices=DOSHA_AFFINITY,
        default='general',
        db_column='dosha_affinity'
    )
    price = models.DecimalField(
        verbose_name=_('Price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column='price'
    )
    stock_quantity = models.IntegerField(
        verbose_name=_('Stock Quantity'),
        validators=[MinValueValidator(0)],
        db_column='stock_quantity',
        default=0
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
        db_table = 'medicines'
        verbose_name_plural = 'Medicines'
        managed = True
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['dosha_affinity']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def reduce_stock(self, quantity: int) -> bool:
        """Reduce medicine stock atomically."""
        if self.stock_quantity < quantity:
            return False
        self.stock_quantity -= quantity
        self.save()
        return True
    
    def increase_stock(self, quantity: int):
        """Increase medicine stock."""
        self.stock_quantity += quantity
        self.save()

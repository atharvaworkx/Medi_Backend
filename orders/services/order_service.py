from django.db import transaction
from django.core.exceptions import ValidationError
from medicines.models import Medicine
from orders.models import Order, OrderItem, Subscription
from typing import List, Dict


class OrderService:
    """Service to handle order operations."""
    
    @staticmethod
    @transaction.atomic
    def checkout(patient, items: List[Dict]) -> tuple:
        """
        Process checkout and create order.
        
        Args:
            patient: User instance
            items: List of dicts with medicine_id and quantity
        
        Returns:
            Tuple of (order, success_dict or error_dict)
        """
        try:
            # Validate and reserve stock
            order_items_data = []
            total_amount = 0
            
            for item in items:
                medicine = Medicine.objects.select_for_update().get(id=item['medicine_id'])
                quantity = item['quantity']
                
                # Check stock
                if medicine.stock_quantity < quantity:
                    return None, {
                        'status': 'error',
                        'message': f'Insufficient stock for {medicine.name}'
                    }
                
                # Calculate total
                item_total = medicine.price * quantity
                total_amount += item_total
                
                order_items_data.append({
                    'medicine': medicine,
                    'quantity': quantity,
                    'price': medicine.price
                })
            
            # Create order
            order = Order.objects.create(
                patient=patient,
                total_amount=total_amount,
                status='pending',
                payment_status='pending'
            )
            
            # Create order items and reduce stock
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    medicine=item_data['medicine'],
                    quantity=item_data['quantity'],
                    price_at_purchase=item_data['price']
                )
                
                # Atomically reduce stock
                item_data['medicine'].reduce_stock(item_data['quantity'])
            
            return order, {
                'status': 'success',
                'order_id': order.id,
                'total_amount': str(total_amount)
            }
        
        except Medicine.DoesNotExist:
            return None, {
                'status': 'error',
                'message': 'One or more medicines not found'
            }
        except Exception as e:
            return None, {
                'status': 'error',
                'message': str(e)
            }
    
    @staticmethod
    def cancel_order(order: Order) -> Dict:
        """Cancel order and restore stock."""
        if order.status in ['delivered', 'cancelled']:
            return {
                'status': 'error',
                'message': 'Cannot cancel delivered or already cancelled orders'
            }
        
        # Restore stock for all items
        for item in order.items.all():
            if item.medicine:
                item.medicine.increase_stock(item.quantity)
        
        order.status = 'cancelled'
        order.payment_status = 'refunded'
        order.save()
        
        return {
            'status': 'success',
            'message': 'Order cancelled and stock restored'
        }

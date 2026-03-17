from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Users
from profiles.models import UserProfile


@receiver(post_save, sender=Users)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created"""
    if created:
        UserProfile.objects.get_or_create(
            userId=instance,
            defaults={'fullName': f"{instance.firstName} {instance.lastName}"}
        )


@receiver(post_save, sender=Users)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile exists"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

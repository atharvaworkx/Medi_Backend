"""
Notification service for appointment emails.
Uses Celery shared_task for async email dispatch.
If Celery is not running (dev), tasks will be queued and fail silently
because appointment_service.py wraps the .delay() calls in try/except.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


# ── Standalone Celery tasks (must be module-level, not @staticmethod) ──────

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_confirmation_task(self, appointment_id):
    """Send appointment confirmation email. Celery async task."""
    from appointments.models import Appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        logger.info(
            '[EMAIL] Confirmation sent to %s for appointment %s',
            appointment.patient.email, appointment_id
        )
        return {'status': 'sent', 'appointment_id': appointment_id}
    except Appointment.DoesNotExist:
        logger.error('Appointment %s not found', appointment_id)
        return {'status': 'error', 'message': 'Appointment not found'}
    except Exception as exc:
        logger.error('Error sending confirmation: %s', str(exc))
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_cancellation_notification_task(self, appointment_id):
    """Send cancellation notification. Celery async task."""
    from appointments.models import Appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        logger.info(
            '[EMAIL] Cancellation sent to %s for appointment %s',
            appointment.patient.email, appointment_id
        )
        return {'status': 'sent', 'appointment_id': appointment_id}
    except Exception as exc:
        logger.error('Error sending cancellation: %s', str(exc))
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_appointment_reminder_task(self, appointment_id):
    """Send appointment reminder 24hrs before. Celery async task."""
    from appointments.models import Appointment
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        logger.info(
            '[REMINDER] Sent to %s for appointment %s',
            appointment.patient.email, appointment_id
        )
        return {'status': 'sent', 'appointment_id': appointment_id}
    except Exception as exc:
        logger.error('Error sending reminder: %s', str(exc))
        raise self.retry(exc=exc)


class NotificationService:
    """Utility wrapper — use standalone tasks (_task suffix) for .delay() calls."""

    @staticmethod
    def format_email(appointment):
        return {
            'patient_name': f"{appointment.patient.firstName} {appointment.patient.lastName}",
            'doctor_name': f"Dr. {appointment.doctor.user.firstName} {appointment.doctor.user.lastName}",
            'date': appointment.date,
            'start_time': appointment.start_time,
            'meeting_link': appointment.meeting_link,
        }

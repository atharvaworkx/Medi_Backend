import logging
from datetime import datetime, timedelta
from typing import Tuple, Dict

from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from appointments.models import Appointment
from doctors.models import Doctor, DoctorAvailability

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service to handle appointment operations."""
    
    DEFAULT_SLOT_DURATION = 30  # minutes
    
    @staticmethod
    def check_doctor_availability(doctor: Doctor, date, start_time) -> bool:
        """Check if doctor is available on given date and time."""
        day_of_week = date.weekday()
        
        slots = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )
        
        for slot in slots:
            if slot.start_time <= start_time < slot.end_time:
                return True
        
        return False
    
    @staticmethod
    def check_slot_conflict(doctor: Doctor, date, start_time, end_time) -> bool:
        """Check if slot is already booked."""
        conflict = Appointment.objects.filter(
            doctor=doctor,
            date=date,
            status__in=['booked', 'confirmed']
        ).filter(
            models.Q(start_time__lt=end_time) &
            models.Q(end_time__gt=start_time)
        ).exists()
        
        return conflict
    
    @staticmethod
    def get_available_slots(doctor: Doctor, date) -> list:
        """Get all available slots for a doctor on a given date."""
        day_of_week = date.weekday()
        
        availability = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )
        
        slots = []
        for slot in availability:
            booked = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                status__in=['booked', 'confirmed']
            ).values_list('start_time', 'end_time')
            
            current_time = slot.start_time
            while current_time < slot.end_time:
                end_time = (datetime.combine(date, current_time) + 
                           timedelta(minutes=AppointmentService.DEFAULT_SLOT_DURATION)).time()
                
                is_booked = any(
                    booked_start <= current_time < booked_end 
                    for booked_start, booked_end in booked
                )
                
                if not is_booked and end_time <= slot.end_time:
                    slots.append({
                        'start_time': current_time.isoformat(),
                        'end_time': end_time.isoformat(),
                        'available': True
                    })
                
                current_time = end_time
        
        return slots
    
    @staticmethod
    @transaction.atomic
    def book_appointment(patient, doctor_id: int, date, start_time, notes: str = None) -> Tuple[Appointment, Dict]:
        """Book appointment with conflict checking and transaction lock."""
        try:
            doctor = Doctor.objects.select_for_update().get(id=doctor_id)
            
            if not doctor.is_available or not doctor.is_verified:
                raise ValidationError(_('Doctor is not available'))
            
            end_time = (datetime.combine(date, start_time) + 
                       timedelta(minutes=AppointmentService.DEFAULT_SLOT_DURATION)).time()
            
            if not AppointmentService.check_doctor_availability(doctor, date, start_time):
                raise ValidationError(_('Doctor is not available at this time'))
            
            if AppointmentService.check_slot_conflict(doctor, date, start_time, end_time):
                raise ValidationError(_('Slot is already booked'))
            
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                start_time=start_time,
                end_time=end_time,
                notes=notes,
                status='booked'
            )
            
            meeting_link = AppointmentService.generate_meeting_link(appointment)
            # Use update() to set meeting_link without triggering full_clean() again
            Appointment.objects.filter(id=appointment.id).update(meeting_link=meeting_link)
            appointment.meeting_link = meeting_link
            
            logger.info(
                'Appointment booked: id=%s patient=%s doctor=%s date=%s',
                appointment.id, patient.id, doctor_id, date
            )
            
            # Dispatch Celery notification (non-blocking; fails gracefully if Celery is down)
            try:
                from appointments.services.notification_service import send_appointment_confirmation_task
                transaction.on_commit(
                    lambda: send_appointment_confirmation_task.delay(appointment_id)
                )
            except Exception:
                logger.warning('Celery not available — skipping appointment confirmation email')
            
            return appointment, {
                'status': 'success',
                'appointment_id': appointment.id,
                'date': str(appointment.date),
                'start_time': str(appointment.start_time),
                'doctor_name': f"Dr. {doctor.user.firstName} {doctor.user.lastName}",
                'meeting_link': meeting_link
            }
        
        except ValidationError as e:
            logger.warning('Appointment booking failed for patient=%s doctor=%s: %s', patient.id, doctor_id, e)
            return None, {
                'status': 'error',
                'message': str(e)
            }
    
    @staticmethod
    def generate_meeting_link(appointment: Appointment) -> str:
        """Generate placeholder meeting link."""
        return f"https://meet.medipilot.local/appt/{appointment.id}"
    
    @staticmethod
    def cancel_appointment(appointment: Appointment, reason: str = None) -> Dict:
        """Cancel appointment if allowed."""
        if not appointment.can_be_cancelled():
            return {
                'status': 'error',
                'message': _('Cannot cancel - appointment is within 24 hours or already completed')
            }
        
        appointment.status = 'cancelled'
        appointment.cancellation_reason = reason
        # Use update() to avoid triggering full_clean() which would reject
        # past-dated appointments during cancellation
        Appointment.objects.filter(id=appointment.id).update(
            status='cancelled',
            cancellation_reason=reason
        )
        logger.info('Appointment cancelled: id=%s reason=%s', appointment.id, reason)

        try:
            from appointments.services.notification_service import send_cancellation_notification_task
            send_cancellation_notification_task.delay(appointment.id)
        except Exception:
            logger.warning('Celery not available — skipping cancellation notification')
        
        return {
            'status': 'success',
            'message': _('Appointment cancelled successfully')
        }

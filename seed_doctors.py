from doctors.models import Doctor, Specialization, DoctorAvailability
from users.models import Users
from datetime import time

def seed_doctors():
    # 1. Seed Specializations
    specs = [
        {'name': 'Vata Specialist', 'related_dosha': 'vata', 'category': 'specialized', 'description': 'Expert in balancing Vata dosha related issues.'},
        {'name': 'Pitta Specialist', 'related_dosha': 'pitta', 'category': 'specialized', 'description': 'Expert in balancing Pitta dosha related issues.'},
        {'name': 'Kapha Specialist', 'related_dosha': 'kapha', 'category': 'specialized', 'description': 'Expert in balancing Kapha dosha related issues.'},
        {'name': 'General Ayurveda', 'related_dosha': 'general', 'category': 'preventive', 'description': 'Overall health and wellbeing through Ayurveda.'},
    ]
    
    spec_objs = {}
    for s_data in specs:
        name = s_data.pop('name')
        spec, _ = Specialization.objects.get_or_create(name=name, defaults=s_data)
        spec_objs[name] = spec

    # 2. Create Doctor Users
    dr_users = [
        {'email': 'dr.sharma@medipilot.local', 'firstName': 'Rajesh', 'lastName': 'Sharma', 'phone': '9876500001'},
        {'email': 'dr.patil@medipilot.local', 'firstName': 'Snehal', 'lastName': 'Patil', 'phone': '9876500002'},
    ]
    
    doctors_data = [
        {
            'user_email': 'dr.sharma@medipilot.local',
            'spec_name': 'Vata Specialist',
            'exp': 12,
            'fee': 500,
            'bio': 'Passionate about Ayurvedic healing.'
        },
        {
            'user_email': 'dr.patil@medipilot.local',
            'spec_name': 'Pitta Specialist',
            'exp': 8,
            'fee': 400,
            'bio': 'Helping patients find their inner balance.'
        }
    ]

    for u_data in dr_users:
        email = u_data.pop('email')
        user, created = Users.objects.get_or_create(
            email=email,
            defaults={**u_data, 'level': 2} # Assume 2 is for professional/doctor
        )
        if created:
            user.set_password('doctor123')
            user.save()
            
    # 3. Create Doctor Profiles
    for d_data in doctors_data:
        user = Users.objects.get(email=d_data['user_email'])
        spec = spec_objs[d_data['spec_name']]
        doctor, _ = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'specialization': spec,
                'years_of_experience': d_data['exp'],
                'consultation_fee': d_data['fee'],
                'bio': d_data['bio'],
                'is_verified': True
            }
        )
        
        # 4. Add Availability (Mon-Fri, 9 AM - 5 PM)
        for day in range(5):
            DoctorAvailability.objects.get_or_create(
                doctor=doctor,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0)
            )

    print("Doctors and Specializations seeded successfully!")

if __name__ == "__main__":
    seed_doctors()

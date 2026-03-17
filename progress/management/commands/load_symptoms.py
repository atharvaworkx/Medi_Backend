from django.core.management.base import BaseCommand
from progress.models import Symptom


class Command(BaseCommand):
    help = 'Load initial symptoms data'
    
    def handle(self, *args, **options):
        symptoms_data = [
            ('Bloating', 'digestive', 'kapha'),
            ('Constipation', 'digestive', 'vata'),
            ('Acidity', 'digestive', 'pitta'),
            ('Skin rash', 'skin', 'pitta'),
            ('Eczema', 'skin', 'vata'),
            ('Anxiety', 'mental', 'vata'),
            ('Depression', 'mental', 'kapha'),
            ('Headache', 'general', 'pitta'),
            ('Fatigue', 'general', 'kapha'),
            ('Insomnia', 'general', 'vata'),
            ('Joint pain', 'joint', 'vata'),
            ('Cough', 'respiratory', 'kapha'),
        ]
        
        created_count = 0
        for name, category, dosha in symptoms_data:
            symptom, created = Symptom.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'related_dosha': dosha,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Loaded {created_count} new symptoms'))

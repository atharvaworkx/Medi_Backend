from prescriptions.models import Prescription
from ai_reports.models import HealthAssessmentReport
from medicines.models import Medicine
from typing import List, Dict


class MedicineRecommender:
    """Service to recommend medicines based on prescription and health profile."""
    
    DOSHA_MEDICINE_MAPPING = {
        'vata': ['Ashwagandha', 'Triphala', 'Ginger', 'Sesame Oil'],
        'pitta': ['Neem', 'Turmeric', 'Brahmi', 'Coconut Oil'],
        'kapha': ['Ginger Tea', 'Honey', 'Fenugreek', 'Mustard Oil'],
    }
    
    @staticmethod
    def recommend_medicines(prescription: Prescription) -> List[Dict]:
        """
        Recommend medicines based on prescription and AI report.
        
        Returns:
            List of recommended medicines with relevance scores.
        """
        patient = prescription.patient
        
        # Get latest health assessment report
        health_report = HealthAssessmentReport.objects.filter(userId=patient).first()
        
        # Determine dominant dosha from prakriti result
        dominant_dosha = 'general'
        if health_report and health_report.prakritResult:
            prakriti = health_report.prakritResult
            vata = prakriti.get('vata', 0)
            pitta = prakriti.get('pitta', 0)
            kapha = prakriti.get('kapha', 0)
            
            max_score = max(vata, pitta, kapha)
            if max_score > 0:
                if vata == max_score:
                    dominant_dosha = 'vata'
                elif pitta == max_score:
                    dominant_dosha = 'pitta'
                elif kapha == max_score:
                    dominant_dosha = 'kapha'
        
        # Get recommended medicine names
        recommended_names = MedicineRecommender.DOSHA_MEDICINE_MAPPING.get(dominant_dosha, [])
        
        # Query medicines using django.db.models.Q
        from django.db.models import Q
        medicines = Medicine.objects.filter(
            is_active=True,
            category__in=['ayurvedic', 'herbal']
        ).filter(
            Q(name__in=recommended_names) |
            Q(dosha_affinity=dominant_dosha)
        )
        
        # Rank by dosha affinity and stock
        recommendations = []
        for medicine in medicines:
            relevance_score = MedicineRecommender._calculate_relevance(
                medicine, 
                dominant_dosha
            )
            
            if medicine.stock_quantity > 0:
                recommendations.append({
                    'medicine_id': medicine.id,
                    'name': medicine.name,
                    'category': medicine.category,
                    'dosage_info': medicine.dosage_info,
                    'price': str(medicine.price),
                    'stock_available': medicine.stock_quantity,
                    'dosha_affinity': medicine.dosha_affinity,
                    'relevance_score': relevance_score,
                    'description': medicine.description
                })
        
        # Sort by relevance score descending
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        return recommendations
    
    @staticmethod
    def _calculate_relevance(medicine: Medicine, dominant_dosha: str) -> float:
        """Calculate relevance score for a medicine."""
        score = 0.0
        
        # Direct dosha match
        if medicine.dosha_affinity == dominant_dosha:
            score += 1.0
        elif medicine.dosha_affinity == 'general':
            score += 0.5
        
        # Stock availability bonus
        if medicine.stock_quantity > 10:
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0


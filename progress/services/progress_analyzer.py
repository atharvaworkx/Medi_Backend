import logging
from django.db.models import Avg, Max, Min
from progress.models import DailyHealthLog, SymptomLog
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ProgressAnalyzer:
    """Service to analyze patient progress and health trends."""
    
    IMPROVEMENT_THRESHOLD = 20  # percentage improvement
    RISK_THRESHOLD_STRESS = 8  # stress level out of 10
    RISK_THRESHOLD_DIGESTION = 3  # digestion quality out of 10
    
    @staticmethod
    def get_period_logs(user, days: int = 30) -> tuple:
        """Get health logs for specified period."""
        start_date = datetime.now().date() - timedelta(days=days)
        logs = DailyHealthLog.objects.filter(
            user=user,
            date__gte=start_date
        ).order_by('date')
        return list(logs), start_date, datetime.now().date()
    
    @staticmethod
    def calculate_trend(logs: List[DailyHealthLog], metric: str) -> Dict:
        """Calculate trend for a metric."""
        if not logs or len(logs) < 2:
            return {'trend': 'insufficient_data', 'change': 0}
        
        first_half = logs[:len(logs)//2]
        second_half = logs[len(logs)//2:]
        
        if metric == 'energy':
            first_avg = sum(l.energy_level for l in first_half) / len(first_half)
            second_avg = sum(l.energy_level for l in second_half) / len(second_half)
        elif metric == 'digestion':
            first_avg = sum(l.digestion_quality for l in first_half) / len(first_half)
            second_avg = sum(l.digestion_quality for l in second_half) / len(second_half)
        elif metric == 'stress':
            first_avg = sum(l.stress_level for l in first_half) / len(first_half)
            second_avg = sum(l.stress_level for l in second_half) / len(second_half)
        elif metric == 'sleep':
            first_avg = sum(l.sleep_hours for l in first_half) / len(first_half)
            second_avg = sum(l.sleep_hours for l in second_half) / len(second_half)
        else:
            return {'trend': 'unknown', 'change': 0}
        
        change = ((second_avg - first_avg) / first_avg * 100) if first_avg else 0
        
        if metric == 'stress':
            trend = 'improving' if change < -ProgressAnalyzer.IMPROVEMENT_THRESHOLD else (
                'worsening' if change > ProgressAnalyzer.IMPROVEMENT_THRESHOLD else 'stable'
            )
        else:
            trend = 'improving' if change > ProgressAnalyzer.IMPROVEMENT_THRESHOLD else (
                'worsening' if change < -ProgressAnalyzer.IMPROVEMENT_THRESHOLD else 'stable'
            )
        
        return {
            'trend': trend,
            'change': round(change, 2),
            'first_avg': round(first_avg, 2),
            'second_avg': round(second_avg, 2)
        }
    
    @staticmethod
    def detect_risk_flags(logs: List[DailyHealthLog], user) -> List[str]:
        """Detect potential risk conditions."""
        flags = []
        
        if not logs:
            return flags
        
        recent_logs = logs[-7:] if len(logs) >= 7 else logs
        
        if len(recent_logs) > 0:
            avg_stress = sum(l.stress_level for l in recent_logs) / len(recent_logs)
            if avg_stress >= ProgressAnalyzer.RISK_THRESHOLD_STRESS:
                flags.append(f'High stress detected (avg: {avg_stress:.1f}/10) for past 7 days')
            
            avg_digestion = sum(l.digestion_quality for l in recent_logs) / len(recent_logs)
            if avg_digestion <= ProgressAnalyzer.RISK_THRESHOLD_DIGESTION:
                flags.append(f'Poor digestion quality (avg: {avg_digestion:.1f}/10)')
            
            avg_sleep = sum(l.sleep_hours for l in recent_logs) / len(recent_logs)
            if avg_sleep < 6:
                flags.append(f'Insufficient sleep (avg: {avg_sleep:.1f} hours)')
            
            avg_energy = sum(l.energy_level for l in recent_logs) / len(recent_logs)
            if avg_energy < 4:
                flags.append(f'Very low energy levels (avg: {avg_energy:.1f}/10)')
        
        symptom_logs = SymptomLog.objects.filter(
            daily_log__user=user,
            daily_log__in=logs
        ).select_related('symptom')
        
        for symptom_log in symptom_logs:
            if symptom_log.severity >= 4:
                flags.append(f'Severe {symptom_log.symptom.name} ({symptom_log.severity}/5)')
        
        return flags
    
    @classmethod
    def calculate_improvement_score(cls, logs: List[DailyHealthLog]) -> int:
        """Calculate overall improvement score (0-100)."""
        if not logs or len(logs) < 2:
            return 50
        
        energy_trend = cls.calculate_trend(logs, 'energy')
        digestion_trend = cls.calculate_trend(logs, 'digestion')
        stress_trend = cls.calculate_trend(logs, 'stress')
        sleep_trend = cls.calculate_trend(logs, 'sleep')
        
        score = 50
        
        for metric_trend in [energy_trend, digestion_trend, stress_trend, sleep_trend]:
            if metric_trend['trend'] == 'improving':
                score += 6.25
            elif metric_trend['trend'] == 'worsening':
                score -= 6.25
        
        return max(0, min(100, int(score)))
    
    @classmethod
    def generate_analytics(cls, user, days: int = 30) -> Dict:
        """Generate comprehensive analytics report."""
        logs, start_date, end_date = cls.get_period_logs(user, days)
        
        if not logs:
            return {
                'period': f'{days}_days',
                'trend_summary': 'No health data available. Start logging daily health metrics.',
                'improvement_score': 0,
                'risk_flags': [],
                'recommended_action': 'Begin daily health tracking',
                'stats': {}
            }
        
        energy_trend = cls.calculate_trend(logs, 'energy')
        digestion_trend = cls.calculate_trend(logs, 'digestion')
        stress_trend = cls.calculate_trend(logs, 'stress')
        sleep_trend = cls.calculate_trend(logs, 'sleep')
        
        risk_flags = cls.detect_risk_flags(logs, user)
        improvement_score = cls.calculate_improvement_score(logs)
        
        trends = [energy_trend, digestion_trend, stress_trend, sleep_trend]
        improving_count = sum(1 for t in trends if t['trend'] == 'improving')
        
        if improving_count >= 3:
            trend_summary = f'Great progress! {improving_count}/4 main health metrics are improving.'
        elif improving_count >= 2:
            trend_summary = f'Good progress. {improving_count}/4 metrics improving, monitor others.'
        elif improving_count >= 1:
            trend_summary = 'Slow progress on some metrics. Focus on stress and digestion.'
        else:
            trend_summary = 'Health metrics are declining. Seek professional guidance.'
        
        if risk_flags:
            recommended_action = 'Schedule consultation - concerning health trends detected'
        elif improvement_score < 40:
            recommended_action = 'Increase focus on healthy habits and lifestyle changes'
        elif improvement_score < 70:
            recommended_action = 'Continue current routine, minor adjustments recommended'
        else:
            recommended_action = 'Maintain current healthy practices'
        
        return {
            'period': f'{days}_days',
            'date_range': {
                'start': str(start_date),
                'end': str(end_date)
            },
            'trend_summary': trend_summary,
            'improvement_score': improvement_score,
            'risk_flags': risk_flags,
            'recommended_action': recommended_action,
            'stats': {
                'total_logs': len(logs),
                'energy': energy_trend,
                'digestion': digestion_trend,
                'stress': stress_trend,
                'sleep': sleep_trend
            }
        }

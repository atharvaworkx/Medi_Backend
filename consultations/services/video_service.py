from abc import ABC, abstractmethod
from typing import Dict, Optional


class VideoProvider(ABC):
    """Abstract base class for video meeting providers."""
    
    @abstractmethod
    def create_meeting(self, appointment_id: int, doctor_name: str, patient_name: str) -> Dict:
        """Create a video meeting and return meeting details."""
        pass
    
    @abstractmethod
    def delete_meeting(self, provider_meeting_id: str) -> bool:
        """Delete a video meeting."""
        pass
    
    @abstractmethod
    def validate_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Validate if participant can access meeting."""
        pass
    
    @abstractmethod
    def generate_token(self, meeting_id: str, participant_role: str) -> str:
        """Generate access token for participant."""
        pass


class MockVideoProvider(VideoProvider):
    """Mock video provider for development/testing."""
    
    def create_meeting(self, appointment_id: int, doctor_name: str, patient_name: str) -> Dict:
        """Create a mock meeting link."""
        meeting_id = f"mock_{appointment_id}_{hash((doctor_name, patient_name)) % 10000}"
        return {
            'provider_meeting_id': meeting_id,
            'meeting_link': f"https://meet.medipilot.local/consultation/{meeting_id}",
            'start_url': f"https://meet.medipilot.local/consultation/{meeting_id}?role=host",
            'join_url': f"https://meet.medipilot.local/consultation/{meeting_id}?role=participant",
        }
    
    def delete_meeting(self, provider_meeting_id: str) -> bool:
        """Delete mock meeting (no-op)."""
        return True
    
    def validate_participant(self, meeting_id: str, participant_id: str) -> bool:
        """Validate participant (mock)."""
        return True
    
    def generate_token(self, meeting_id: str, participant_role: str) -> str:
        """Generate mock access token."""
        return f"mock_token_{meeting_id}_{participant_role}"


class VideoServiceFactory:
    """Factory to select video provider based on environment."""
    
    _providers = {
        'mock': MockVideoProvider,
        # 'zoom': 'ZoomVideoProvider',  # Ready for future implementation
        # 'twilio': 'TwilioVideoProvider',  # Ready for future implementation
    }
    
    @staticmethod
    def get_provider(provider_name: str = 'mock') -> VideoProvider:
        """Get video provider instance."""
        import os
        provider = provider_name or os.getenv('VIDEO_PROVIDER', 'mock')
        
        if provider not in VideoServiceFactory._providers:
            raise ValueError(f"Unknown video provider: {provider}")
        
        provider_class = VideoServiceFactory._providers[provider]
        return provider_class()

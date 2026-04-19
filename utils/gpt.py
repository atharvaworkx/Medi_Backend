import os
import json
import logging
from django.conf import settings
import requests
from PIL import Image
from io import BytesIO

from src.vault import credentials

logger = logging.getLogger(__name__)

GROK_API_KEY = os.environ.get("GROK_API_KEY")
if not GROK_API_KEY:
    env = os.environ.get("ENV", "dev")
    GROK_API_KEY = credentials.get(env, {}).get("GROK_API_KEY", "")

if GROK_API_KEY:
    logger.info("Grok AI configured successfully")
else:
    logger.warning("GROK_API_KEY not found in environment or vault")

def generate_health_assessment(quiz_data, image_urls):
    """
    Main function to generate health assessment report using Grok AI.
    Analyzes quiz answers and uploaded health images.
    """
    try:
        if not GROK_API_KEY:
            raise ValueError("GROK_API_KEY is not configured")

        prompt = _construct_health_prompt(quiz_data)
        
        messages = [{"role": "user", "content": prompt}]
        
        for img_type, url in image_urls.items():
            if url:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        img_base64 = _image_to_base64(img)
                        messages[0]["content"] += f"\n\nImage of {img_type} (base64): {img_base64[:100]}..."
                except Exception as e:
                    logger.error(f"Failed to load image from {url}: {e}")

        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-2-vision-1212",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            logger.error(f"Grok API error: {response.status_code} - {response.text}")
            return None
        
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        report_data = json.loads(content)
        return report_data

    except Exception as e:
        logger.error(f"Error in generate_health_assessment: {e}")
        return None


def _image_to_base64(img):
    """Convert PIL Image to base64 string"""
    import base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def _construct_health_prompt(quiz_data):
    """
    Constructs a detailed prompt for Grok to analyze health data.
    """
    format_example = {
        "overallScore": 85,
        "healthScores": {
            "Digestion": 70,
            "Immunity": 75,
            "Sleep": 60,
            "Stress": 55,
            "Energy": 80
        },
        "prakritResult": {"vata": 30, "pitta": 40, "kapha": 30},
        "vikritResult": {"vata": 35, "pitta": 35, "kapha": 30},
        "digestiveRisk": {"riskLevel": "low/medium/high", "details": ["..."]},
        "skinRisk": {"riskLevel": "low/medium/high", "details": ["..."]},
        "mentalHealthRisk": {"riskLevel": "low/medium/high", "details": ["..."]},
        "imageAnalysisResults": {"iris": "...", "nails": "...", "hair": "...", "skin": "..."},
        "overallSummary": "...",
        "dominantPrakriti": "Vata/Pitta/Kapha/Sama",
        "dominantVikriti": "Vata/Pitta/Kapha/Sama",
        "recommendations": ["...", "..."],
        "riskFlags": ["...", "..."],
        "isCritical": False
    }

    prompt = f"""
You are an expert Ayurvedic Health Consultant and Medical Vision Specialist specializing in 'Ashta Vidha Pariksha' (The Eight-fold Ayurvedic Clinical Examination).
Analyze the following patient health data which includes lifestyle quiz answers and images for visual examination.

INPUT DATA:
- Quiz Results (Prakriti/Vikriti scores): {json.dumps(quiz_data.get('prakritiScores'), indent=2)}
- Question & Answers: {json.dumps(quiz_data.get('responses'), indent=2)}
- Visual Evidence: Iris, Nails, Hair, and Skin images provided.

AYURVEDIC ANALYSIS TASKS:
1. PRAKRITI & VIKRITI: Evaluate the balance of Vata, Pitta, and Kapha based on the lifestyle data.
2. DRIK PARIKSHA (Eye/Iris): Analyze the iris for clarity, coloring, and signs of systemic health.
3. AKRITI PARIKSHA (Forms): Analyze Nails (for ridges, moons, color) and Hair (for texture, strength) as indicators of nutrient absorption and hormonal balance.
4. SPARSHA PARIKSHA (Skin): Analyze skin texture and appearance for Pitta or Vata imbalances.
5. JIHVA PARIKSHA (Tongue - if provided): Check for coating or discoloration.

GUIDELINES:
- POSITIVE BIAS: The report MUST be leaned towards the positive side (healthy). Focus on the user's vitality and natural strengths.
- REASONING: Explain how their current habits are supporting their health score.
- OPTIMIZATION: Describe imbalances as 'minor deviations' or 'opportunities for further vitality'.
- Keep the overall score relatively high (75-95 range) to encourage the user, unless critical indicators are found.
- Provide actionable Ayurvedic recommendations (Ahar/Diet, Vihar/Lifestyle, and simple herbal suggestions).

REPORT FORMAT:
You MUST return ONLY a valid JSON object matching the following structure:
{json.dumps(format_example, indent=2)}

Ensure the 'imageAnalysisResults' contains observations for each image provided. If an image type is missing, omit it from the results or note it as 'Not provided'.
The response should be strictly JSON.
"""
    return prompt

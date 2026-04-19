import os
import uuid
from users.models import Users
from quiz.models import QuizQuestion, QuizOption, QuizResponse, QuizResult
from images.models import HealthImage
from ai_reports.models import HealthAssessmentReport
from django.utils import timezone

def seed_data():
    email = "a@gmail.com"
    user_id = "1f068402-19cc-4a81-9af3-52fba0056901"

    # 1. Get or Create User
    user, created = Users.objects.update_or_create(
        email=email,
        defaults={
            'id': uuid.UUID(user_id),
            'firstName': 'Atharva',
            'lastName': 'S',
            'is_active': True,
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"Created user: {email}")
    else:
        print(f"User already exists: {email}")

    # 2. Create/Update Quiz Questions and Options if they don't exist
    if QuizQuestion.objects.count() == 0:
        questions = [
            ("How do you feel after a heavy meal?", "prakriti", 1),
            ("How is your sleep quality?", "prakriti", 2),
            ("How describes your skin texture?", "prakriti", 3),
            ("Do you feel energetic in the morning?", "vikriti", 4)
        ]
        options_data = [
            ["Light and energetic", "Sluggish and heavy", "Sleepy"],
            ["Deep and sound", "Light and interrupted", "Too much sleep"],
            ["Dry and thin", "Oily and soft", "Thick and smooth"],
            ["Yes, very much", "Sometimes", "No, feeling dull"]
        ]

        for i, (q_text, cat, order) in enumerate(questions):
            q = QuizQuestion.objects.create(
                questionText=q_text,
                category=cat,
                order=order,
                questionType='multipleChoice'
            )
            for opt_text in options_data[i]:
                QuizOption.objects.create(
                    questionId=q,
                    optionText=opt_text,
                    optionValue=opt_text.lower().replace(" ", "_"),
                    order=1,
                    scoreData={'vata': 0.3, 'pitta': 0.4, 'kapha': 0.3}
                )
        print("Created sample questions and options")

    # 3. Create Quiz Responses
    questions_list = QuizQuestion.objects.all()
    for q in questions_list:
        opt = q.options.first()
        if opt:
            QuizResponse.objects.update_or_create(
                userId=user,
                questionId=q,
                defaults={
                    'selectedOptionId': opt,
                    'responseValue': opt.optionText
                }
            )
    print("Created/Updated quiz responses")

    # 4. Create Quiz Result
    QuizResult.objects.update_or_create(
        userId=user,
        defaults={
            'prakritScores': {'vata': 35, 'pitta': 45, 'kapha': 20},
            'vikritScores': {'vata': 40, 'pitta': 30, 'kapha': 30},
            'dominantPrakriti': 'Pitta',
            'dominantVikriti': 'Vata',
            'completedAt': timezone.now()
        }
    )
    print("Created/Updated quiz result")

    # 5. Create Health Images
    image_types = ['iris', 'nails', 'hair', 'skin']
    urls = {
        'iris': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Human-iris.jpg/800px-Human-iris.jpg',
        'nails': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Hand_nails.jpg/800px-Hand_nails.jpg',
        'hair': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Hair_follicle.jpg/800px-Hair_follicle.jpg',
        'skin': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Skin_structure.jpg/800px-Skin_structure.jpg'
    }

    for img_type in image_types:
        HealthImage.objects.update_or_create(
            userId=user,
            imageType=img_type,
            defaults={
                'imageUrl': urls.get(img_type),
                'processingStatus': 'completed',
                'aiProcessed': True,
                'aiResults': {'status': 'healthy', 'observation': f'Normal {img_type} appearance'}
            }
        )
    print("Created/Updated health images")

    # 6. Create Health Assessment Report
    report_data = {
        'overallScore': 92,
        'prakritResult': {'vata': 35, 'pitta': 45, 'kapha': 20},
        'vikritResult': {'vata': 40, 'pitta': 30, 'kapha': 30},
        'digestiveRisk': {
            'riskLevel': 'low', 
            'details': ['Excellent Metabolic Fire (Agni)', 'Regular bowel movements indicated']
        },
        'skinRisk': {
            'riskLevel': 'low', 
            'details': ['High skin elasticity', 'Proper hydration levels']
        },
        'mentalHealthRisk': {
            'riskLevel': 'low', 
            'details': ['Calm mental state', 'High resilience']
        },
        'imageAnalysisResults': {
            'iris': 'Clear iris structure, no systemic toxicity signs.',
            'nails': 'Strong pink nail beds, no ridges or moons issues.',
            'hair': 'Lustrous texture, strong roots.',
            'skin': 'Even tone, good moisture retention.'
        },
        'overallSummary': (
            "Congratulations! Your health assessment shows exceptional vitality. "
            "Your predominant Pitta constitution is well-balanced. "
            "Your visual markers (Iris and Nails) reflect a high state of Ojas (strength). "
            "Keep up your current wellness routine as it seems highly effective for your body type."
        ),
        'recommendations': [
            'Maintain early morning walks in nature',
            'Continue with fresh pomegranate and coconut water',
            'Abhyanga (Oil massage) once a week with coconut oil',
            'Practice sheetali pranayama to keep pitta in check during heat'
        ],
        'riskFlags': [],
        'isCritical': False,
    }

    HealthAssessmentReport.objects.update_or_create(
        userId=user,
        defaults=report_data
    )
    print("Created/Updated health assessment report")
    print("Data seeding completed successfully!")

if __name__ == "__main__":
    seed_data()

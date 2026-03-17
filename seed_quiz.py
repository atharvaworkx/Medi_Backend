from quiz.models import QuizQuestion, QuizOption

def seed_quiz():
    # 1. Body Frame
    q1, created = QuizQuestion.objects.get_or_create(
        questionText="How do you describe your body frame?",
        questionType="multipleChoice",
        category="prakriti",
        order=1
    )
    if created:
        QuizOption.objects.create(questionId=q1, optionText="Small/Thin", optionValue="thin", scoreData={"vata": 1, "pitta": 0, "kapha": 0}, order=1)
        QuizOption.objects.create(questionId=q1, optionText="Medium/Muscular", optionValue="medium", scoreData={"vata": 0, "pitta": 1, "kapha": 0}, order=2)
        QuizOption.objects.create(questionId=q1, optionText="Large/Broad", optionValue="broad", scoreData={"vata": 0, "pitta": 0, "kapha": 1}, order=3)

    # 2. Appetite
    q2, created = QuizQuestion.objects.get_or_create(
        questionText="How would you describe your appetite?",
        questionType="multipleChoice",
        category="prakriti",
        order=2
    )
    if created:
        QuizOption.objects.create(questionId=q2, optionText="Irregular/Variable", optionValue="irregular", scoreData={"vata": 1, "pitta": 0, "kapha": 0}, order=1)
        QuizOption.objects.create(questionId=q2, optionText="Strong/Intense", optionValue="strong", scoreData={"vata": 0, "pitta": 1, "kapha": 0}, order=2)
        QuizOption.objects.create(questionId=q2, optionText="Slow/Steady", optionValue="steady", scoreData={"vata": 0, "pitta": 0, "kapha": 1}, order=3)

    print("Quiz seeded successfully!")

if __name__ == "__main__":
    seed_quiz()

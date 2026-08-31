from sqlalchemy.orm import Session
from app.models.context import Context
from app.models.user import User
from app.schemas.question import QuestionCreate
from app.repositories.question import question_repository
from app.services.llm_service import llm_service
from fastapi import HTTPException

class QuestionService:
    async def generate_and_save_questions(self, db: Session, context: Context, user: User):
        # 1. Préparer les données
        profile_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "education_level": user.education_level,
            "field": user.field,
            "objective": user.objective
        }
        cv_text = context.cv.extracted_text if context.cv and context.cv.extracted_text else ""
        job_text = context.job.extracted_text if context.job and context.job.extracted_text else ""
        notes = context.notes or ""

        # 2. Appel au LLM
        llm_response = await llm_service.generate_questions(profile_data, cv_text, job_text, notes)

        # 3. Validation et enregistrement
        if "questions" not in llm_response:
            raise HTTPException(status_code=500, detail="Format JSON invalide du LLM")

        questions_to_create = []
        for i, q in enumerate(llm_response["questions"]):
            questions_to_create.append(QuestionCreate(
                context_id=context.id,
                text=q.get("text", "Question sans texte"),
                category=q.get("category", "general"),
                difficulty=q.get("difficulty", "medium"),
                order_index=i,
                expected_duration_seconds=q.get("expected_duration_seconds", 120)
            ))

        return question_repository.create_many(db, questions_to_create)

    def get_context_questions(self, db: Session, context_id: int):
        return question_repository.get_by_context_id(db, context_id)

question_service = QuestionService()
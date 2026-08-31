from typing import List
from sqlalchemy.orm import Session
from app.models.question import Question
from app.schemas.question import QuestionCreate

class QuestionRepository:
    def create(self, db: Session, question_in: QuestionCreate) -> Question:
        db_question = Question(
            context_id=question_in.context_id,
            text=question_in.text,
            category=question_in.category,
            difficulty=question_in.difficulty,
            order_index=question_in.order_index,
            expected_duration_seconds=question_in.expected_duration_seconds
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question

    def create_many(self, db: Session, questions_in: List[QuestionCreate]) -> List[Question]:
        db_questions = [
            Question(
                context_id=q.context_id,
                text=q.text,
                category=q.category,
                difficulty=q.difficulty,
                order_index=q.order_index,
                expected_duration_seconds=q.expected_duration_seconds
            )
            for q in questions_in
        ]
        db.add_all(db_questions)
        db.commit()
        for q in db_questions:
            db.refresh(q)
        return db_questions

    def get_by_context_id(self, db: Session, context_id: int) -> List[Question]:
        return db.query(Question).filter(Question.context_id == context_id).order_by(Question.order_index.asc()).all()

question_repository = QuestionRepository()
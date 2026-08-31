import json
import logging
import httpx
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY or settings.GROQ_API_KEY or settings.GEMINI_API_KEY
        
        if settings.GROQ_API_KEY:
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-8b-instant" # Modèle gratuit
        elif settings.GEMINI_API_KEY:
            self.api_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            self.model = "gemini-3.6-flash" # Modèle de Google gratuit et performant
        else:
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4o-mini"

    async def generate_questions(self, profile: dict, cv_text: str, job_text: str, notes: str) -> dict:
        if not self.api_key:
            # Fallback for testing if no key is provided
            return {
                "questions": [
                    {
                        "text": "[Mock] Parlez-moi de votre expérience indiquée sur le CV.",
                        "category": "experience",
                        "difficulty": "medium",
                        "expected_duration_seconds": 120
                    }
                ]
            }

        prompt = f"""
Tu es un expert en recrutement. Ton but est de générer des questions d'entretien pertinentes basées sur les informations suivantes:
PROFIL: {json.dumps(profile)}
CV: {cv_text[:2000]}
OFFRE: {job_text[:2000]}
NOTES: {notes}

Génère 3 à 5 questions réparties dans les catégories: technical, behavioral, motivation, experience.
Réponds STRICTEMENT en JSON avec ce format:
{{
  "questions": [
    {{
      "text": "la question",
      "category": "technical",
      "difficulty": "medium",
      "expected_duration_seconds": 120
    }}
  ]
}}
"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "response_format": {"type": "json_object"},
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()
                return json.loads(data["choices"][0]["message"]["content"])
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            raise HTTPException(status_code=502, detail=f"Erreur lors de la génération avec l'IA: {str(e)}")

llm_service = LLMService()
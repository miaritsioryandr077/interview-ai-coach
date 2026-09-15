import json
import logging
import httpx
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY or settings.GROQ_API_KEY or settings.GEMINI_API_KEY
        # On détermine le provider utilisé (priorité: GROQ > GEMINI > OPENAI)
        if settings.GROQ_API_KEY:
            self.provider = "groq"
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-8b-instant"  # Modèle gratuit
        elif settings.GEMINI_API_KEY:
            # API native Gemini (et non l'endpoint OpenAI-compatible).
            # Les nouvelles clés "AQ.Ab..." ne fonctionnent QUE sur l'API native.
            self.provider = "gemini"
            # Liste de repli : si un modèle est indisponible (404 déprécié ou
            # 503/429 surchargé), on essaie automatiquement le suivant.
            self.models = [
                "gemini-flash-latest",
                "gemini-3.6-flash",
                "gemini-2.5-flash",
                "gemini-3.5-flash",
            ]
            self.model = self.models[0]
            self.gemini_base_url = (
                "https://generativelanguage.googleapis.com/v1beta/models"
            )
        else:
            self.provider = "openai"
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
            if self.provider == "gemini":
                content = await self._call_gemini(prompt)
            else:
                content = await self._call_openai_compatible(prompt)

            # Nettoyage si le LLM rajoute des backticks markdown (ex: ```json ... ```)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM Error: {repr(e)}")
            raise HTTPException(status_code=502, detail=f"Erreur lors de la génération avec l'IA: {repr(e)}")

    async def _call_gemini(self, prompt: str) -> str:
        # Appelle l'API native Gemini en essayant chaque modèle de repli.
        last_error = None
        async with httpx.AsyncClient() as client:
            for model in self.models:
                url = f"{self.gemini_base_url}/{model}:generateContent"
                try:
                    response = await client.post(
                        url,
                        headers={
                            "Content-Type": "application/json",
                            "x-goog-api-key": self.api_key,
                        },
                        json={
                            "contents": [{"parts": [{"text": prompt}]}],
                            "generationConfig": {
                                "maxOutputTokens": 1500,
                                "responseMimeType": "application/json",
                            },
                        },
                        timeout=120.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    self.model = model
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    logger.warning(f"Gemini model {model} failed ({status}), trying next...")
                    last_error = e
                    # On ne réessaie que pour les erreurs transitoires/dépréciation
                    if status not in (404, 429, 500, 503):
                        raise
            if last_error:
                raise last_error
            raise HTTPException(status_code=502, detail="Aucun modèle Gemini disponible")

    async def _call_openai_compatible(self, prompt: str) -> str:
        # Appelle un endpoint OpenAI-compatible (Groq / OpenAI).
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1500,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

llm_service = LLMService()
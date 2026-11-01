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
                "gemini-3.5-flash-lite",
                "gemini-flash-lite-latest",
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
            # Récupération du corps de la réponse HTTP le cas échéant (Google),
            # pour identifier la véritable cause d'un 400/4xx.
            error_detail = repr(e)
            response_body = None
            resp = getattr(e, "response", None)
            if resp is not None:
                try:
                    response_body = resp.text
                except Exception:
                    response_body = None
            if response_body:
                logger.error("LLM Error: %s | Response body: %s", repr(e), response_body[:1000])
                error_detail = f"{repr(e)} | Response body: {response_body[:500]}"
            else:
                logger.error(f"LLM Error: {repr(e)}")
            raise HTTPException(status_code=502, detail=f"Erreur lors de la génération avec l'IA: {error_detail}")

    async def analyze_interview(self, qa_list: list[dict]) -> dict:
        """Analyse une session d'entretien (un seul appel Gemini)."""
        import asyncio
        from app.services.prompts.analyze_interview import build_analyze_prompt

        prompt = build_analyze_prompt(qa_list)

        async def _attempt() -> str:
            if self.provider == "gemini":
                return await self._call_gemini(prompt, timeout=60.0)
            return await self._call_openai_compatible(prompt)

        last_exc = None
        for attempt in range(2):
            try:
                content = await _attempt()
                break
            except Exception as e:
                last_exc = e
                # Retry unique sur timeout / 5xx ; pas sur 429 ni 400.
                status = getattr(getattr(e, "response", None), "status_code", None)
                is_timeout = isinstance(e, (httpx.TimeoutException, httpx.ReadTimeout))
                is_5xx = status is not None and 500 <= status < 600
                if attempt == 0 and (is_timeout or is_5xx):
                    await asyncio.sleep(1.0)
                    continue
                raise
        else:
            raise last_exc

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        import json as _json
        return _json.loads(content)


    async def _call_gemini(self, prompt: str, timeout: float = 120.0, response_schema: dict | None = None) -> str:
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
                                "maxOutputTokens": 4096,
                                "responseMimeType": "application/json",
                                **({"responseSchema": response_schema} if response_schema else {}),
                            },
                        },
                        timeout=timeout,
                    )
                    response.raise_for_status()
                    data = response.json()
                    # Extraction sécurisée du texte (un modèle "thinking" peut
                    # renvoyer un content vide si les tokens sont consommés).
                    try:
                        candidate = (data.get("candidates") or [{}])[0]
                        content_obj = candidate.get("content") or {}
                        parts = content_obj.get("parts") or []
                        text = parts[0].get("text") if parts else None
                    except (IndexError, AttributeError, TypeError):
                        text = None
                    if not text:
                        logger.warning(
                            "Gemini model %s returned empty content, trying next...",
                            model,
                        )
                        continue
                    self.model = model
                    return text
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    # Récupération du corps de la réponse Google pour diagnostic
                    # (sans jamais journaliser la clé API ni les en-têtes sensibles).
                    try:
                        error_body = e.response.text
                    except Exception:
                        error_body = "<unreadable>"
                    logger.warning(
                        "Gemini model %s failed (HTTP %s). Response body: %s",
                        model,
                        status,
                        error_body[:1000],
                    )
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
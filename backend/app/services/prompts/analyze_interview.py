"""Prompt builder for interview analysis.

Versionnable et testable isolément.
"""

PROMPT_VERSION = "1.0"


def build_analyze_prompt(qa_list: list[dict]) -> str:
    """Construit le prompt d'analyse pour une session d'entretien.

    qa_list : liste de dicts {"question_id": int, "question": str, "answer": str | None}.
    """
    blocks = []
    for item in qa_list:
        qid = item["question_id"]
        question = item["question"]
        answer = item.get("answer")
        if answer and answer.strip():
            blocks.append(
                f"Question {qid}: {question}\nRéponse: {answer.strip()}"
            )
        else:
            blocks.append(f"Question {qid}: {question}\nRéponse: (non répondue)")

    joined = "\n\n".join(blocks)

    return f"""Tu es un coach en entretien professionnel. Analyse les réponses
d'un candidat à un entretien simulé et produis une évaluation structurée.

CRITÈRES DE SCORING (note /10 pour chacun) :
- pertinence : la réponse répond-elle à la question posée, avec un
  exemple concret, sans hors-sujet ?
- structure : introduction / développement / conclusion, ordre logique.
- clarte : phrases courtes, vocabulaire précis, pas d'ambiguïté.
- vocabulaire : registre adapté à un entretien professionnel.

RÈGLES :
- Score global = synthèse des 4 critères (0 à 10).
- Ne surévalue pas les réponses très courtes (1 ligne) : note modérée
  sauf si la réponse est parfaitement ciblée.
- Pour chaque réponse non vide : donne un feedback court (1-2 phrases)
  et une "meilleure reformulation" CONCRÈTE (pas un conseil générique),
  en reprenant le fond de la réponse du candidat.
- Pour les questions non répondues (marquées "(non répondue)") :
  answered=false, score=null, feedback=null, improved_answer=null.
- strengths/weaknesses/advice : listes de chaînes courtes (3 à 5 items).

QUESTIONS ET RÉPONSES :
{joined}

Réponds STRICTEMENT en JSON avec ce format :
{{
  "overall_score": 0.0,
  "criteria": {{
    "pertinence": 0.0,
    "structure": 0.0,
    "clarte": 0.0,
    "vocabulaire": 0.0
  }},
  "strengths": [""],
  "weaknesses": [""],
  "advice": [""],
  "responses": [
    {{
      "question_id": 0,
      "question": "",
      "answered": true,
      "score": 0.0,
      "feedback": "",
      "improved_answer": ""
    }}
  ]
}}
"""
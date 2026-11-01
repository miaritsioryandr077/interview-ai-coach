from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.models.session import Session, SessionStatus
from app.repositories.context import context_repository
from app.repositories.session import session_repository
from app.schemas.progress import (
    CriteriaAverages,
    EvolutionItem,
    PreparationProgressResponse,
    ProgressResponse,
)


class ProgressService:
    def _completed_sessions(self, db, user_id, context_id=None):
        sessions = session_repository.get_by_user_id(db, user_id)
        out = []
        for s in sessions:
            if s.status != SessionStatus.COMPLETED:
                continue
            if context_id is not None and s.context_id != context_id:
                continue
            out.append(s)
        return out

    def _analyzed(self, sessions):
        return [s for s in sessions if isinstance(s.analysis, dict)]

    def _title(self, s):
        ctx = getattr(s, "context", None)
        if ctx is not None:
            job = getattr(ctx, "job", None)
            if job is not None and getattr(job, "original_filename", None):
                return job.original_filename
        return f"Préparation #{s.context_id}"

    def _build(self, sessions_all_completed, analyzed, preparation_id=None):
        total_completed = len(sessions_all_completed)
        total_analyzed = len(analyzed)
        if total_analyzed > 0:
            avg_overall = sum(
                (s.analysis or {}).get("overall_score", 0) for s in analyzed
            ) / total_analyzed
            crit = {"pertinence": [], "structure": [], "clarte": [], "vocabulaire": []}
            for s in analyzed:
                c = (s.analysis or {}).get("criteria", {}) or {}
                for k in crit:
                    v = c.get(k)
                    if isinstance(v, (int, float)):
                        crit[k].append(v)
            avg_crit = CriteriaAverages(
                pertinence=(sum(crit["pertinence"]) / len(crit["pertinence"])) if crit["pertinence"] else None,
                structure=(sum(crit["structure"]) / len(crit["structure"])) if crit["structure"] else None,
                clarte=(sum(crit["clarte"]) / len(crit["clarte"])) if crit["clarte"] else None,
                vocabulaire=(sum(crit["vocabulaire"]) / len(crit["vocabulaire"])) if crit["vocabulaire"] else None,
            )
        else:
            avg_overall = None
            avg_crit = CriteriaAverages()

        evolution = []
        for s in sorted(analyzed, key=lambda x: (x.ended_at or x.started_at)):
            evolution.append(
                EvolutionItem(
                    session_id=s.id,
                    date=(s.ended_at or s.started_at),
                    overall_score=(s.analysis or {}).get("overall_score", 0),
                    preparation_title=self._title(s),
                )
            )

        if preparation_id is not None:
            return PreparationProgressResponse(
                preparation_id=preparation_id,
                total_completed=total_completed,
                total_analyzed=total_analyzed,
                average_overall=avg_overall,
                average_by_criterion=avg_crit,
                evolution=evolution,
            )
        return ProgressResponse(
            total_completed=total_completed,
            total_analyzed=total_analyzed,
            average_overall=avg_overall,
            average_by_criterion=avg_crit,
            evolution=evolution,
        )

    def get_progress(self, db, user):
        completed = self._completed_sessions(db, user.id)
        analyzed = self._analyzed(completed)
        return self._build(completed, analyzed)

    def get_preparation_progress(self, db, user, context_id):
        ctx = context_repository.get_by_id_and_user(db, context_id, user.id)
        if not ctx:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préparation non trouvée")
        completed = self._completed_sessions(db, user.id, context_id)
        analyzed = self._analyzed(completed)
        return self._build(completed, analyzed, preparation_id=context_id)


progress_service = ProgressService()
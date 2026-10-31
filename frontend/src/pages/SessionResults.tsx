import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Loader2, ArrowLeft, Home, CheckCircle2, AlertCircle } from "lucide-react";
import { sessionService } from "../services/sessionService";
import { contextService } from "../services/contextService";
import { Context } from "../types/context";
import { InterviewSession as InterviewSessionData } from "../types/session";

export const SessionResults: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<InterviewSessionData | null>(null);
  const [context, setContext] = useState<Context | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!sessionId) return;
      try {
        setLoading(true);
        const s = await sessionService.getSession(Number(sessionId));
        setSession(s);
        try {
          const ctxs = await contextService.getMyContexts();
          setContext(ctxs.find((c) => c.id === s.context_id) || null);
        } catch {
        }
      } catch (err: any) {
        setError(err.message || "Impossible de charger les résultats.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-gray-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin" />
        Chargement des résultats...
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded-lg px-4 py-3">
          <AlertCircle className="w-5 h-5" />
          {error || "Session introuvable."}
        </div>
        <button
          onClick={() => navigate("/history")}
          className="mt-4 text-brand-400 hover:text-brand-300 text-sm"
        >
          Retour à l'historique
        </button>
      </div>
    );
  }
  const answeredMap = new Map(session.responses.map((r) => [r.question_id, r]));

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Résultats de l'entretien</h1>
        <div className="flex gap-2">
          <button
            onClick={() => navigate("/history")}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition"
          >
            <ArrowLeft className="w-4 h-4" /> Retour à l'historique
          </button>
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition"
          >
            <Home className="w-4 h-4" /> Tableau de bord
          </button>
        </div>
      </div>

      <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-400">Préparation</p>
          <p className="text-white font-medium">{context?.job?.original_filename || `Préparation #${session.context_id}`}</p>
        </div>
        <div>
          <p className="text-gray-400">Statut</p>
          <p className="text-white font-medium">{session.status === "completed" ? "Terminée" : "En cours"}</p>
        </div>
        <div>
          <p className="text-gray-400">Date de début</p>
          <p className="text-white font-medium">{new Date(session.started_at).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-gray-400">Date de fin</p>
          <p className="text-white font-medium">{session.ended_at ? new Date(session.ended_at).toLocaleString() : "—"}</p>
        </div>
        <div>
          <p className="text-gray-400">Questions</p>
          <p className="text-white font-medium">{session.total_questions}</p>
        </div>
        <div>
          <p className="text-gray-400">Réponses enregistrées</p>
          <p className="text-white font-medium">{session.responses.length}</p>
        </div>
      </div>

      <div className="space-y-4">
        {session.questions.map((q, idx) => {
          const resp = answeredMap.get(q.id);
          return (
            <div key={q.id} className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 space-y-3">
              <div className="flex items-start gap-2">
                <span className="text-brand-400 font-semibold">{idx + 1}.</span>
                <p className="text-white">{q.text}</p>
              </div>
              <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Votre réponse :</p>
                {resp ? (
                  <p className="text-gray-200 whitespace-pre-wrap">{resp.text}</p>
                ) : (
                  <p className="text-gray-500 italic">Aucune réponse enregistrée.</p>
                )}
              </div>
              <div className="flex items-center gap-2 text-xs">
                {resp ? (
                  <span className="flex items-center gap-1 text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Réponse enregistrée
                  </span>
                ) : (
                  <span className="flex items-center gap-1 text-amber-400">
                    <AlertCircle className="w-3.5 h-3.5" /> Sans réponse
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SessionResults;
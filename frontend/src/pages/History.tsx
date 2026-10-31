import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Play, Eye, PlusCircle, Clock, AlertCircle } from "lucide-react";
import { sessionService } from "../services/sessionService";
import { contextService } from "../services/contextService";
import { Context } from "../types/context";
import { InterviewSession as InterviewSessionData } from "../types/session";

export const History: React.FC = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<InterviewSessionData[]>([]);
  const [contexts, setContexts] = useState<Context[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState<Record<number, boolean>>({});

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [ctxs, sess] = await Promise.all([
          contextService.getMyContexts(),
          sessionService.getMySessions(),
        ]);
        setContexts(ctxs);
        setSessions(sess.sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime()));
      } catch (err: any) {
        setError(err.message || "Impossible de charger l'historique.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const contextById = (id: number) => contexts.find((c) => c.id === id);

  const handleNewSession = async (contextId: number) => {
    try {
      setStarting((prev) => ({ ...prev, [contextId]: true }));
      const session = await sessionService.startSession(contextId);
      navigate(`/interview/${session.id}`);
    } catch (err: any) {
      setError(err.message || "Impossible de démarrer une nouvelle simulation.");
    } finally {
      setStarting((prev) => ({ ...prev, [contextId]: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-gray-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin" />
        Chargement de l'historique...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
          <Clock className="w-7 h-7 text-brand-500" />
          Historique des entretiens
        </h1>
        <p className="text-gray-400 mt-1">
          Retrouvez toutes vos simulations, consultez vos résultats ou reprenez une session inachevée.
        </p>
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 text-red-400 bg-red-950/30 border border-red-900/50 rounded-lg px-4 py-3">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="text-center py-16 bg-gray-800/40 border border-gray-700 rounded-xl">
          <Clock className="w-10 h-10 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-300 font-medium">Aucun entretien pour le moment.</p>
          <p className="text-gray-500 text-sm mt-1">
            Lancez votre première simulation depuis le tableau de bord.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((s) => {
            const ctx = contextById(s.context_id);
            const title = ctx?.job?.original_filename || `Préparation #${s.context_id}`;
            const isInProgress = s.status === "in_progress";
            return (
              <div
                key={s.id}
                className="bg-gray-800/60 border border-gray-700 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-white font-semibold">{title}</h3>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        isInProgress
                          ? "bg-amber-500/20 text-amber-400"
                          : "bg-emerald-500/20 text-emerald-400"
                      }`}
                    >
                      {isInProgress ? "En cours" : "Terminée"}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm">
                    {new Date(s.started_at).toLocaleString()}{" "}
                    {s.ended_at ? `• Terminée le ${new Date(s.ended_at).toLocaleString()}` : ""}
                  </p>
                  <p className="text-gray-500 text-xs">
                    {s.total_questions} question(s) • {s.responses.filter((r) => r.text && r.text.trim()).length} réponse(s)
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {isInProgress ? (
                    <button
                      onClick={() => navigate(`/interview/${s.id}`)}
                      className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition"
                    >
                      <Play className="w-4 h-4" /> Reprendre
                    </button>
                  ) : (
                    <button
                      onClick={() => navigate(`/sessions/${s.id}/results`)}
                      className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition"
                    >
                      <Eye className="w-4 h-4" /> Voir les résultats
                    </button>
                  )}
                  <button
                    onClick={() => handleNewSession(s.context_id)}
                    disabled={starting[s.context_id]}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition disabled:opacity-50"
                  >
                    {starting[s.context_id] ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <PlusCircle className="w-4 h-4" />
                    )}
                    Nouvelle simulation
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default History;

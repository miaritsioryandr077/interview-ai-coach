import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Loader2,
  MicOff,
  Send,
  Sparkles,
} from "lucide-react";
import { InterviewSession as InterviewSessionData } from "../types/session";
import { sessionService } from "../services/sessionService";
import { contextService } from "../services/contextService";
import { Context } from "../types/context";

export const InterviewSession: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<InterviewSessionData | null>(null);
  const [context, setContext] = useState<Context | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answerText, setAnswerText] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finished, setFinished] = useState(false);

  // Chargement initial de la session et du contexte (titre de la préparation).
  useEffect(() => {
    const load = async () => {
      if (!sessionId) return;
      try {
        setLoading(true);
        const s = await sessionService.getSession(Number(sessionId));
        setSession(s);

        // Reprise : on recharge les réponses déjà enregistrées.
        const restored: Record<number, string> = {};
        s.responses.forEach((r) => {
          restored[r.question_id] = r.text;
        });
        setAnswers(restored);

        // Positionne sur la première question sans réponse.
        const firstUnanswered = s.questions.findIndex((q) => !restored[q.id]);
        setCurrentIndex(firstUnanswered === -1 ? 0 : firstUnanswered);

        if (s.status === "completed") {
          setFinished(true);
        }

        try {
          const ctxs = await contextService.getMyContexts();
          setContext(ctxs.find((c) => c.id === s.context_id) || null);
        } catch {
          // Le titre de la préparation est optionnel.
        }
      } catch (err: any) {
        setError(
          err.message || "Impossible de charger la session d'entretien.",
        );
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [sessionId]);

  const currentQuestion = session?.questions[currentIndex];
  const total = session?.questions.length ?? 0;
  const isLast = total > 0 && currentIndex === total - 1;

  // Le champ du textarea suit la question affichée.
  useEffect(() => {
    if (currentQuestion) {
      setAnswerText(answers[currentQuestion.id] ?? "");
    }
  }, [currentIndex, currentQuestion?.id]);

  const answeredCount = useMemo(
    () =>
      session
        ? session.questions.filter((q) => answers[q.id]?.trim()).length
        : 0,
    [session, answers],
  );

  const handleValidate = async () => {
    if (!session || !currentQuestion || saving) return;
    if (!answerText.trim()) {
      setError("Veuillez saisir une réponse avant de valider.");
      return;
    }

    try {
      setSaving(true);
      setError(null);
      await sessionService.saveResponse(
        session.id,
        currentQuestion.id,
        answerText,
      );

      setAnswers((prev) => ({ ...prev, [currentQuestion.id]: answerText }));

      // Passe automatiquement à la question suivante si elle existe.
      if (currentIndex < total - 1) {
        setCurrentIndex(currentIndex + 1);
      }
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'enregistrement de la réponse.");
    } finally {
      setSaving(false);
    }
  };

  const handleComplete = async () => {
    if (!session || completing) return;
    try {
      setCompleting(true);
      setError(null);
      await sessionService.completeSession(session.id);
      setFinished(true);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la clôture de l'entretien.");
    } finally {
      setCompleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-gray-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin" />
        Chargement de l'entretien...
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="flex items-center gap-2 text-red-400 bg-red-500/10 px-4 py-3 rounded-lg border-red-500/20">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      </div>
    );
  }

  // --- Écran de fin : aucun score ni analyse IA pour cette version. ---
  if (finished) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 space-y-6 text-center">
        <div className="flex justify-center">
          <div className="p-4 bg-emerald-500/10 rounded-full">
            <CheckCircle2 className="w-12 h-12 text-emerald-400" />
          </div>
        </div>
        <h1 className="text-3xl font-extrabold text-white">
          Entretien terminé
        </h1>
        <p className="text-gray-400">
          Vous avez répondu à {answeredCount} question
          {answeredCount > 1 ? "s" : ""} sur {total}. Vos réponses ont bien été
          enregistrées.
        </p>
        <div className="flex items-center justify-center gap-3 pt-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="px-6 py-3 bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-xl transition"
          >
            Retour au tableau de bord
          </button>
        </div>
      </div>
    );
  }

  if (!session || !currentQuestion) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-gray-400">
        Aucune question disponible pour cette session.
      </div>
    );
  }

  const contextTitle = context
    ? `${context.cv?.original_filename ?? "CV"} • ${context.job?.original_filename ?? "Offre"}`
    : `Préparation #${session.context_id}`;

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-6">
      {/* En-tête : titre de la préparation + progression */}
      <div className="space-y-3">
        <h1 className="text-2xl font-extrabold text-white truncate">
          {contextTitle}
        </h1>
        <div className="flex items-center justify-between text-sm">
          <span className="font-semibold text-brand-400">
            Question {currentIndex + 1} / {total}
          </span>
          <span className="text-gray-500">
            {answeredCount} réponse{answeredCount > 1 ? "s" : ""} enregistrée
            {answeredCount > 1 ? "s" : ""}
          </span>
        </div>
        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-brand-600 to-indigo-500 transition-all"
            style={{ width: `${(answeredCount / Math.max(total, 1)) * 100}%` }}
          />
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 px-4 py-3 rounded-lg border-red-500/20">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Question courante */}
      <div className="glass-card p-6 rounded-2xl border-gray-800 space-y-4">
        <div className="flex gap-2 text-xs font-semibold uppercase tracking-wider">
          <span className="bg-brand-500/20 text-brand-400 px-2 py-0.5 rounded">
            {currentQuestion.category}
          </span>
          <span
            className={`px-2 py-0.5 rounded ${
              currentQuestion.difficulty === "hard"
                ? "bg-red-500/20 text-red-400"
                : currentQuestion.difficulty === "easy"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : "bg-amber-500/20 text-amber-400"
            }`}
          >
            {currentQuestion.difficulty}
          </span>
        </div>

        <p className="text-lg text-gray-100 leading-relaxed flex items-start gap-2">
          <Sparkles className="w-5 h-5 text-amber-400 flex-shrink-0 mt-1" />
          {currentQuestion.text}
        </p>

        <div className="pt-2">
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Votre réponse :
          </label>
          <textarea
            value={answerText}
            onChange={(e) => setAnswerText(e.target.value)}
            rows={8}
            disabled={saving}
            placeholder="Rédigez votre réponse ici..."
            className="w-full bg-gray-900 border-gray-700 rounded-lg px-4 py-3 text-white focus:border-brand-500 outline-none resize-y disabled:opacity-60"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-gray-500">
          <MicOff className="w-4 h-4" />
          Entretien textuel uniquement — la saisie vocale arrivera plus tard.
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
          disabled={currentIndex === 0 || saving}
          className="px-4 py-2.5 text-sm font-medium text-gray-300 hover:text-white bg-gray-800/60 hover:bg-gray-800 rounded-lg transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Question précédente
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={handleValidate}
            disabled={saving || !answerText.trim()}
            className="flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Enregistrement...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" /> Valider la réponse
              </>
            )}
          </button>

          {isLast ? (
            <button
              onClick={handleComplete}
              disabled={completing || saving}
              className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition disabled:opacity-50"
            >
              {completing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Clôture...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" /> Terminer l'entretien
                </>
              )}
            </button>
          ) : (
            <button
              onClick={() => setCurrentIndex(currentIndex + 1)}
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-white font-semibold rounded-lg transition disabled:opacity-50"
            >
              Question suivante <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterviewSession;

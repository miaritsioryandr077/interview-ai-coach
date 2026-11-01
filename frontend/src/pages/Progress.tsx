import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Loader2, TrendingUp, BarChart3 } from "lucide-react";
import { progressService } from "../services/progressService";

export const Progress: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const d = await progressService.getProgress();
        setData(d);
      } catch (err: any) {
        setError(err.message || "Impossible de charger la progression.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] text-gray-400 gap-3">
        <Loader2 className="w-6 h-6 animate-spin" />
        Chargement de la progression...
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-8 text-red-400">{error}</div>
    );
  }

  const hasData = (data?.total_analyzed ?? 0) > 0;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
          <TrendingUp className="w-7 h-7 text-brand-500" />
          Ma progression
        </h1>
        <p className="text-gray-400 mt-1">
          Suivez vos performances dans le temps, par préparation et globalement.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400 text-sm">Entretiens terminés</p>
          <p className="text-2xl font-bold text-white">{data?.total_completed ?? 0}</p>
        </div>
        <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400 text-sm">Sessions analysées</p>
          <p className="text-2xl font-bold text-white">{data?.total_analyzed ?? 0}</p>
        </div>
        <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-5">
          <p className="text-gray-400 text-sm">Score moyen</p>
          <p className="text-2xl font-bold text-brand-400">
            {data?.average_overall != null ? `${data.average_overall}/10` : "—"}
          </p>
        </div>
      </div>

      {!hasData ? (
        <div className="text-center py-16 bg-gray-800/40 border border-gray-700 rounded-xl">
          <BarChart3 className="w-10 h-10 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-300 font-medium">
            Aucune session analysée pour le moment.
          </p>
          <p className="text-gray-500 text-sm mt-1">
            Terminez un entretien et lancez l'analyse pour voir votre progression.
          </p>
          <Link
            to="/dashboard"
            className="inline-block mt-4 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition"
          >
            Aller au tableau de bord
          </Link>
        </div>
      ) : (
        <>
          <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-5">
            <p className="text-gray-300 font-medium mb-3">Moyennes par critère</p>
            <div className="space-y-2">
              {(["pertinence", "structure", "clarte", "vocabulaire"] as const).map((c) => {
                const v = data?.average_by_criterion?.[c];
                return (
                  <div key={c} className="flex items-center gap-3">
                    <span className="text-gray-400 text-sm w-24 capitalize">{c}</span>
                    <div className="flex-1 bg-gray-900/60 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-brand-500 h-2 rounded-full"
                        style={{ width: v != null ? `${(v / 10) * 100}%` : "0%" }}
                      />
                    </div>
                    <span className="text-white text-sm w-10 text-right">
                      {v != null ? `${v}/10` : "—"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-5">
            <p className="text-gray-300 font-medium mb-3">Évolution du score</p>
            <div className="space-y-2">
              {data.evolution.map((e: any) => (
                <div
                  key={e.session_id}
                  className="flex items-center justify-between bg-gray-900/60 border border-gray-700 rounded-lg px-4 py-2"
                >
                  <div>
                    <p className="text-white text-sm">{e.preparation_title}</p>
                    <p className="text-gray-500 text-xs">{new Date(e.date).toLocaleString()}</p>
                  </div>
                  <span className="text-brand-400 font-semibold">{e.overall_score}/10</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Progress;
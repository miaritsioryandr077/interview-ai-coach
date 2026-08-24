import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Sparkles, CheckCircle2, ShieldCheck, User as UserIcon, Calendar, Mail } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Welcome Banner */}
      <div className="glass-card rounded-3xl p-8 border border-gray-800 relative overflow-hidden glow-effect">
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold mb-4">
              <Sparkles className="w-3.5 h-3.5" /> Espace Personnel Authentifié
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Bienvenue, {user?.full_name || 'Candidat'} !
            </h1>
            <p className="text-gray-400 mt-2 max-w-2xl text-sm md:text-base">
              Votre authentification JWT de bout en bout est opérationnelle. Vous avez maintenant accès à votre tableau de bord de simulation d'entretiens par Intelligence Artificielle.
            </p>
          </div>
        </div>
      </div>

      {/* Profile & Status Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Account Info */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-brand-600/20 text-brand-400 rounded-xl">
              <UserIcon className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Profil Utilisateur</h3>
              <p className="text-xs text-gray-400">Informations de compte</p>
            </div>
          </div>
          <div className="space-y-3 pt-2 text-sm">
            <div className="flex items-center justify-between border-b border-gray-800/80 pb-2">
              <span className="text-gray-400 flex items-center gap-2">
                <Mail className="w-4 h-4" /> Email:
              </span>
              <span className="font-medium text-white">{user?.email}</span>
            </div>
            <div className="flex items-center justify-between border-b border-gray-800/80 pb-2">
              <span className="text-gray-400 flex items-center gap-2">
                <Calendar className="w-4 h-4" /> Inscrit le:
              </span>
              <span className="font-medium text-white">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Actif'}
              </span>
            </div>
          </div>
        </div>

        {/* Card 2: Security Token Status */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Sécurité JWT</h3>
              <p className="text-xs text-gray-400">Jeton d'accès actif</p>
            </div>
          </div>
          <div className="space-y-2 pt-2 text-sm">
            <p className="text-gray-300">
              Session vérifiée avec succès auprès de l'API FastAPI.
            </p>
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs pt-1">
              <CheckCircle2 className="w-4 h-4" /> En-tête Authorization: Bearer valide
            </div>
          </div>
        </div>

        {/* Card 3: Next Module Teaser */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-xl">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Prochaines Étape</h3>
              <p className="text-xs text-gray-400">Module de Simulation AI</p>
            </div>
          </div>
          <div className="space-y-2 pt-2 text-sm text-gray-300">
            <p>
              Prêt pour l'intégration des modules de dépôt de CV/Offres et de simulation vidéo/vocale d'entretien.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

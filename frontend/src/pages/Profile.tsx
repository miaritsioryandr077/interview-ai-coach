import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchApi } from '../lib/api';
import {
  User as UserIcon,
  Save,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  BookOpen,
  Target,
  Globe,
  Briefcase,
  Mail,
  Calendar,
} from 'lucide-react';
import type { User } from '../context/AuthContext';

// ─── Types ───────────────────────────────────────────────────────────────────

interface ProfileForm {
  first_name: string;
  last_name: string;
  education_level: string;
  field: string;
  objective: string;
  preferred_language: string;
}

// ─── Option maps ──────────────────────────────────────────────────────────────

const EDUCATION_LEVELS = [
  { value: '', label: '— Choisir un niveau —' },
  { value: 'lycee', label: 'Lycée (Bac)' },
  { value: 'licence', label: 'Licence (Bac+3)' },
  { value: 'master', label: 'Master (Bac+5)' },
  { value: 'doctorat', label: 'Doctorat' },
  { value: 'autre', label: 'Autre' },
];

const OBJECTIVES = [
  { value: '', label: '— Choisir un objectif —' },
  { value: 'stage', label: 'Obtenir un stage' },
  { value: 'emploi', label: 'Trouver un emploi' },
  { value: 'concours', label: 'Préparer un concours' },
  { value: 'soutenance', label: 'Préparer une soutenance' },
  { value: 'autre', label: 'Autre' },
];

const LANGUAGES = [
  { value: '', label: '— Choisir une langue —' },
  { value: 'fr', label: '🇫🇷 Français' },
  { value: 'en', label: '🇬🇧 English' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

const labelFor = (options: { value: string; label: string }[], value: string) =>
  options.find((o) => o.value === value)?.label ?? value;

// ─── Component ───────────────────────────────────────────────────────────────

export const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState<ProfileForm>({
    first_name: '',
    last_name: '',
    education_level: '',
    field: '',
    objective: '',
    preferred_language: '',
  });

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Pré-remplir le formulaire avec les données de l'utilisateur
  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name ?? '',
        last_name: user.last_name ?? '',
        education_level: user.education_level ?? '',
        field: user.field ?? '',
        objective: user.objective ?? '',
        preferred_language: user.preferred_language ?? '',
      });
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    // Effacer les messages à la modification
    setSuccessMsg('');
    setErrorMsg('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    setErrorMsg('');

    // Construire le payload en excluant les chaînes vides (envoi null implicite)
    const payload: Record<string, string | null> = {};
    (Object.keys(form) as (keyof ProfileForm)[]).forEach((key) => {
      payload[key] = form[key] !== '' ? form[key] : null;
    });

    try {
      const updated = await fetchApi<User>('/users/me', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      updateUser(updated);
      setSuccessMsg('Profil mis à jour avec succès !');
      // Scroll vers le haut pour afficher le message
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Une erreur est survenue.');
    } finally {
      setSaving(false);
    }
  };

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">

      {/* ── Page Header ── */}
      <div className="glass-card rounded-3xl p-8 border border-gray-800 relative overflow-hidden glow-effect">
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <button
              onClick={() => navigate('/dashboard')}
              className="inline-flex items-center gap-2 text-xs font-medium text-gray-400 hover:text-brand-400 transition mb-4"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Retour au Dashboard
            </button>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold mb-3">
              <UserIcon className="w-3.5 h-3.5" /> Mon Profil
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              {user?.full_name || user?.email || 'Profil Utilisateur'}
            </h1>
            <p className="text-gray-400 mt-1 text-sm">
              Gérez vos informations personnelles et vos préférences d'entretien.
            </p>
          </div>

          {/* Avatar initiales */}
          <div className="flex-shrink-0 w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-600 to-indigo-600 flex items-center justify-center text-3xl font-extrabold text-white shadow-lg shadow-brand-500/20">
            {(user?.first_name?.[0] ?? user?.email?.[0] ?? '?').toUpperCase()}
          </div>
        </div>
      </div>

      {/* ── Feedback alerts ── */}
      {successMsg && (
        <div className="flex items-center gap-3 px-5 py-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-medium animate-fade-in">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
          {successMsg}
        </div>
      )}
      {errorMsg && (
        <div className="flex items-center gap-3 px-5 py-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {errorMsg}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* ── Left: Readonly account info ── */}
        <div className="space-y-4">
          <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
            <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest">Compte</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3">
                <div className="p-2 bg-gray-800 rounded-lg mt-0.5">
                  <Mail className="w-4 h-4 text-brand-400" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs text-gray-500 mb-0.5">Adresse email</p>
                  <p className="text-white font-medium truncate">{user?.email}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="p-2 bg-gray-800 rounded-lg mt-0.5">
                  <Calendar className="w-4 h-4 text-brand-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-0.5">Membre depuis</p>
                  <p className="text-white font-medium">
                    {user?.created_at
                      ? new Date(user.created_at).toLocaleDateString('fr-FR', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                        })
                      : '—'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Résumé profil actuel */}
          <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-3">
            <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest">Résumé</h3>
            <div className="space-y-2 text-sm">
              {[
                { icon: <BookOpen className="w-3.5 h-3.5" />, label: 'Niveau', value: labelFor(EDUCATION_LEVELS, user?.education_level ?? '') },
                { icon: <Briefcase className="w-3.5 h-3.5" />, label: 'Domaine', value: user?.field },
                { icon: <Target className="w-3.5 h-3.5" />, label: 'Objectif', value: labelFor(OBJECTIVES, user?.objective ?? '') },
                { icon: <Globe className="w-3.5 h-3.5" />, label: 'Langue', value: labelFor(LANGUAGES, user?.preferred_language ?? '') },
              ].map(({ icon, label, value }) => (
                <div key={label} className="flex items-center gap-2">
                  <span className="text-brand-400">{icon}</span>
                  <span className="text-gray-500">{label} :</span>
                  <span className="text-gray-200 font-medium">
                    {value && value !== '— Choisir un niveau —' && value !== '— Choisir un objectif —' && value !== '— Choisir une langue —'
                      ? value
                      : <span className="text-gray-600 italic">Non renseigné</span>}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Right: Edit form ── */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
            {/* Form header */}
            <div className="px-6 py-4 border-b border-gray-800 flex items-center gap-3">
              <div className="p-2 bg-brand-500/10 rounded-lg">
                <UserIcon className="w-5 h-5 text-brand-400" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">Modifier le profil</h2>
                <p className="text-xs text-gray-500">Tous les champs sont optionnels</p>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Identité */}
              <fieldset className="space-y-4">
                <legend className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                  Identité
                </legend>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label htmlFor="first_name" className="block text-sm font-medium text-gray-300">
                      Prénom
                    </label>
                    <input
                      id="first_name"
                      name="first_name"
                      type="text"
                      value={form.first_name}
                      onChange={handleChange}
                      placeholder="ex : Marie"
                      className="w-full px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-700 text-white placeholder-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label htmlFor="last_name" className="block text-sm font-medium text-gray-300">
                      Nom
                    </label>
                    <input
                      id="last_name"
                      name="last_name"
                      type="text"
                      value={form.last_name}
                      onChange={handleChange}
                      placeholder="ex : Dupont"
                      className="w-full px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-700 text-white placeholder-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition"
                    />
                  </div>
                </div>
              </fieldset>

              {/* Parcours */}
              <fieldset className="space-y-4">
                <legend className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                  Parcours
                </legend>
                <div className="space-y-1.5">
                  <label htmlFor="education_level" className="block text-sm font-medium text-gray-300">
                    <BookOpen className="inline w-4 h-4 mr-1.5 text-brand-400" />
                    Niveau d'études
                  </label>
                  <select
                    id="education_level"
                    name="education_level"
                    value={form.education_level}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-700 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition appearance-none cursor-pointer"
                  >
                    {EDUCATION_LEVELS.map((opt) => (
                      <option key={opt.value} value={opt.value} className="bg-gray-900">
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label htmlFor="field" className="block text-sm font-medium text-gray-300">
                    <Briefcase className="inline w-4 h-4 mr-1.5 text-brand-400" />
                    Domaine / Filière
                  </label>
                  <input
                    id="field"
                    name="field"
                    type="text"
                    value={form.field}
                    onChange={handleChange}
                    placeholder="ex : Informatique, Finance, Droit…"
                    className="w-full px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-700 text-white placeholder-gray-600 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition"
                  />
                </div>
              </fieldset>

              {/* Préférences */}
              <fieldset className="space-y-4">
                <legend className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                  Préférences d'entretien
                </legend>
                <div className="space-y-1.5">
                  <label htmlFor="objective" className="block text-sm font-medium text-gray-300">
                    <Target className="inline w-4 h-4 mr-1.5 text-brand-400" />
                    Objectif
                  </label>
                  <select
                    id="objective"
                    name="objective"
                    value={form.objective}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-700 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition appearance-none cursor-pointer"
                  >
                    {OBJECTIVES.map((opt) => (
                      <option key={opt.value} value={opt.value} className="bg-gray-900">
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label htmlFor="preferred_language" className="block text-sm font-medium text-gray-300">
                    <Globe className="inline w-4 h-4 mr-1.5 text-brand-400" />
                    Langue préférée
                  </label>
                  <select
                    id="preferred_language"
                    name="preferred_language"
                    value={form.preferred_language}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-xl bg-gray-900/60 border border-gray-700 text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition appearance-none cursor-pointer"
                  >
                    {LANGUAGES.map((opt) => (
                      <option key={opt.value} value={opt.value} className="bg-gray-900">
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </fieldset>
            </div>

            {/* Form footer / submit */}
            <div className="px-6 py-4 border-t border-gray-800 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="px-5 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition"
              >
                Annuler
              </button>
              <button
                id="save-profile-btn"
                type="submit"
                disabled={saving}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed shadow-md hover:shadow-brand-500/25 transition-all"
              >
                {saving ? (
                  <>
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Enregistrement…
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Enregistrer
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

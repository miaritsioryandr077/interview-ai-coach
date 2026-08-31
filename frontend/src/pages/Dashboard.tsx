import React, { useState, useEffect } from 'react';
import { Document } from '../types/document';
import { Context } from '../types/context';
import { Question } from '../types/question';
import { documentService } from '../services/documentService';
import { contextService } from '../services/contextService';
import { BookOpen, PlusCircle, Loader2, Sparkles, AlertCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [cvs, setCvs] = useState<Document[]>([]);
  const [jobs, setJobs] = useState<Document[]>([]);
  const [contexts, setContexts] = useState<Context[]>([]);
  const [questionsMap, setQuestionsMap] = useState<Record<number, Question[]>>({});
  const [generating, setGenerating] = useState<Record<number, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  
  const [selectedCv, setSelectedCv] = useState<string>('');
  const [selectedJob, setSelectedJob] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const docs = await documentService.getMyDocuments();
        setCvs(docs.filter(d => d.document_type === 'cv'));
        setJobs(docs.filter(d => d.document_type === 'job_offer'));
        
        const ctxs = await contextService.getMyContexts();
        setContexts(ctxs);

        // Load existing questions for each context
        const qMap: Record<number, Question[]> = {};
        for (const ctx of ctxs) {
          try {
            const qs = await contextService.getContextQuestions(ctx.id);
            if (qs.length > 0) {
              qMap[ctx.id] = qs;
            }
          } catch (err) {
            // Ignore error if questions not yet generated
          }
        }
        setQuestionsMap(qMap);
      } catch (err) {
        console.error("Erreur lors du chargement des données", err);
      }
    };
    fetchData();
  }, []);

  const handleCreateContext = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCv || !selectedJob) return;
    
    try {
      setLoading(true);
      await contextService.createContext({
        cv_id: parseInt(selectedCv),
        job_id: parseInt(selectedJob),
        notes
      });
      // Refresh contexts
      const ctxs = await contextService.getMyContexts();
      setContexts(ctxs);
      
      // Reset form
      setSelectedCv('');
      setSelectedJob('');
      setNotes('');
      alert("Préparation créée avec succès !");
    } catch (err: any) {
      alert("Erreur lors de la création de la préparation.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuestions = async (contextId: number) => {
    try {
      setGenerating(prev => ({ ...prev, [contextId]: true }));
      setError(null);
      const generatedQs = await contextService.generateQuestions(contextId);
      setQuestionsMap(prev => ({ ...prev, [contextId]: generatedQs }));
    } catch (err: any) {
      console.error(err);
      setError("Erreur lors de la génération des questions. Vérifiez que la clé API est bien configurée.");
    } finally {
      setGenerating(prev => ({ ...prev, [contextId]: false }));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 space-y-8">
      <h1 className="text-3xl font-extrabold text-white">Dashboard & Préparations</h1>
      
      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 px-4 py-3 rounded-lg border border-red-500/20">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Colonne Gauche : Formulaire de création */}
        <div className="glass-card p-6 rounded-2xl border border-gray-800 self-start">
          <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
            <PlusCircle className="w-5 h-5 text-brand-400" />
            Créer une préparation
          </h2>
          <form onSubmit={handleCreateContext} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Sélectionner votre CV</label>
              <select 
                value={selectedCv} 
                onChange={e => setSelectedCv(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-brand-500 outline-none"
                required
              >
                <option value="">-- Choisir un CV --</option>
                {cvs.map(cv => <option key={cv.id} value={cv.id}>{cv.original_filename}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Sélectionner l'offre d'emploi</label>
              <select 
                value={selectedJob} 
                onChange={e => setSelectedJob(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-brand-500 outline-none"
                required
              >
                <option value="">-- Choisir une Offre --</option>
                {jobs.map(job => <option key={job.id} value={job.id}>{job.original_filename}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">Notes (Optionnel)</label>
              <textarea 
                value={notes}
                onChange={e => setNotes(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:border-brand-500 outline-none"
                rows={3}
                placeholder="Ex: Je veux insister sur mes compétences cloud..."
              />
            </div>
            <button 
              type="submit" 
              disabled={loading || !selectedCv || !selectedJob}
              className="w-full py-3 bg-brand-600 hover:bg-brand-500 text-white font-semibold rounded-xl transition disabled:opacity-50"
            >
              {loading ? "Création en cours..." : "Créer la préparation"}
            </button>
          </form>
        </div>

        {/* Colonne Droite : Liste des préparations */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            Mes préparations
          </h2>
          {contexts.length === 0 ? (
            <div className="text-gray-400 p-4 border border-gray-800 rounded-xl bg-gray-900/50">
              Aucune préparation pour l'instant.
            </div>
          ) : (
            contexts.map(ctx => (
              <div key={ctx.id} className="p-5 bg-gray-900/50 rounded-xl border border-gray-800 space-y-4">
                <div className="text-sm text-gray-400 flex justify-between">
                  <span>Créée le {new Date(ctx.created_at).toLocaleDateString()}</span>
                  <span>ID: #{ctx.id}</span>
                </div>
                <div className="text-white bg-gray-800/50 p-3 rounded-lg text-sm">
                  <p><strong>CV:</strong> {ctx.cv?.original_filename}</p>
                  <p><strong>Offre:</strong> {ctx.job?.original_filename}</p>
                  {ctx.notes && <p className="italic text-gray-400 mt-2">"{ctx.notes}"</p>}
                </div>
                
                {/* Generation Area */}
                {!questionsMap[ctx.id] ? (
                  <button
                    onClick={() => handleGenerateQuestions(ctx.id)}
                    disabled={generating[ctx.id]}
                    className="w-full py-2.5 bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30 font-semibold rounded-lg transition flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {generating[ctx.id] ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /> Génération en cours...</>
                    ) : (
                      <><Sparkles className="w-4 h-4" /> Générer les questions</>
                    )}
                  </button>
                ) : (
                  <div className="mt-4 pt-4 border-t border-gray-800">
                    <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-amber-400" />
                      Questions générées
                    </h3>
                    <div className="space-y-3">
                      {questionsMap[ctx.id].map((q, idx) => (
                        <div key={q.id || idx} className="bg-gray-800/80 p-3 rounded-lg border border-gray-700">
                          <div className="flex gap-2 mb-2 text-xs font-semibold uppercase tracking-wider">
                            <span className="bg-brand-500/20 text-brand-400 px-2 py-0.5 rounded">
                              {q.category}
                            </span>
                            <span className={`px-2 py-0.5 rounded ${
                              q.difficulty === 'hard' ? 'bg-red-500/20 text-red-400' :
                              q.difficulty === 'easy' ? 'bg-emerald-500/20 text-emerald-400' :
                              'bg-amber-500/20 text-amber-400'
                            }`}>
                              {q.difficulty}
                            </span>
                          </div>
                          <p className="text-gray-200 text-sm">{idx + 1}. {q.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
        
      </div>
    </div>
  );
};

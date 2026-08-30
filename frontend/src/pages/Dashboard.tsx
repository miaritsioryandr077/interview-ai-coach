import React, { useState, useEffect } from 'react';
import { Document } from '../types/document';
import { Context } from '../types/context';
import { documentService } from '../services/documentService';
import { contextService } from '../services/contextService';
import { BookOpen, PlusCircle, ArrowRight } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [cvs, setCvs] = useState<Document[]>([]);
  const [jobs, setJobs] = useState<Document[]>([]);
  const [contexts, setContexts] = useState<Context[]>([]);
  
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
    } catch (error) {
      alert("Erreur lors de la création de la préparation.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 space-y-8">
      <h1 className="text-3xl font-extrabold text-white">Dashboard & Préparations</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Colonne Gauche : Formulaire de création */}
        <div className="glass-card p-6 rounded-2xl border border-gray-800">
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
              <div key={ctx.id} className="p-4 bg-gray-900/50 rounded-xl border border-gray-800 space-y-2">
                <div className="text-sm text-gray-400 flex justify-between">
                  <span>Créée le {new Date(ctx.created_at).toLocaleDateString()}</span>
                  <span>ID: #{ctx.id}</span>
                </div>
                <div className="text-white">
                  <p><strong>CV:</strong> {ctx.cv?.original_filename}</p>
                  <p><strong>Offre:</strong> {ctx.job?.original_filename}</p>
                </div>
                {ctx.notes && (
                  <p className="text-sm text-gray-400 italic">"{ctx.notes}"</p>
                )}
              </div>
            ))
          )}
        </div>
        
      </div>
    </div>
  );
};

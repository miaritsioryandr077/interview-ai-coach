import React, { useState, useEffect } from 'react';
import { UploadCV } from '../components/UploadCV';
import { DocumentList } from '../components/DocumentList';
import { documentService } from '../services/documentService';
import { Document } from '../types/document';
import { FileText, Briefcase } from 'lucide-react';

export const Documents: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const docs = await documentService.getMyDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Voulez-vous vraiment supprimer ce document ?')) return;
    try {
      await documentService.deleteDocument(id);
      await loadDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Erreur lors de la suppression');
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="flex items-center gap-3">
        <FileText className="w-8 h-8 text-brand-400" />
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Mes documents</h1>
          <p className="text-gray-400 text-sm">Gérez vos CV et offres d'emploi</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Upload CV */}
        <UploadCV 
          onUploadSuccess={loadDocuments}
          title="Uploader un CV"
          uploadFunction={documentService.uploadCV}
          successMessage="CV uploadé avec succès !"
          buttonText="Envoyer mon CV"
        />

        {/* Upload Offre d'emploi */}
        <UploadCV 
          onUploadSuccess={loadDocuments} 
          title="Uploader une offre d'emploi"
          description="Format PDF uniquement (max 5 MB)"
          uploadFunction={documentService.uploadJobOffer}
          successMessage="Offre d'emploi uploadée avec succès !"
          buttonText="Envoyer mon offre d'emploi"
        />
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          Mes CV
        </h2>
        <DocumentList
          documents={documents.filter(d => d.document_type === 'cv')}
          onDelete={handleDelete}
          loading={loading}
        />
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2 mt-8">
          <Briefcase className="w-5 h-5 text-brand-400" />
          Mes offres d'emploi
        </h2>
        <DocumentList
          documents={documents.filter(d => d.document_type === 'job_offer')}
          onDelete={handleDelete}
          loading={loading}
        />
      </div>
    </div>
  );
};
import React, { useState, useEffect } from 'react';
import { UploadCV } from '../components/UploadCV';
import { DocumentList } from '../components/DocumentList';
import { documentService } from '../services/documentService';
import { Document } from '../types/document';
import { FileText } from 'lucide-react';

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

      <UploadCV onUploadSuccess={loadDocuments} />

      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white">Mes CV</h2>
        <DocumentList
          documents={documents.filter(d => d.document_type === 'cv')}
          onDelete={handleDelete}
          loading={loading}
        />
      </div>
    </div>
  );
};
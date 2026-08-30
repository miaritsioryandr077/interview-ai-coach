import React from 'react';
import { File, Trash2, Calendar, FileText, CheckCircle2 } from 'lucide-react';
import { Document, DocumentType } from '../types/document';

interface DocumentListProps {
  documents: Document[];
  onDelete: (id: number) => void;
  loading?: boolean;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, onDelete, loading }) => {
  const getIcon = (type: DocumentType) => {
    return type === DocumentType.CV ? <FileText className="w-5 h-5 text-brand-400" /> : <File className="w-5 h-5 text-indigo-400" />;
  };

  const getTypeLabel = (type: DocumentType) => {
    return type === DocumentType.CV ? 'CV' : 'Offre d\'emploi';
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-400">
        Chargement des documents...
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400 border border-gray-800 rounded-xl">
        <FileText className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p>Aucun document enregistré</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-4 bg-gray-900/50 rounded-xl border border-gray-800 hover:border-gray-700 transition"
        >
          <div className="flex items-center gap-3 min-w-0">
            {getIcon(doc.document_type)}
            <div className="min-w-0">
              <p className="text-white font-medium truncate">{doc.original_filename}</p>
              <div className="flex items-center gap-3 text-xs text-gray-400">
                <span className="capitalize">{getTypeLabel(doc.document_type)}</span>
                <span>•</span>
                <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                <span>•</span>
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {new Date(doc.uploaded_at).toLocaleDateString('fr-FR')}
                </div>
                {doc.extracted_text && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1 text-emerald-400 bg-emerald-400/10 px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider">
                      <CheckCircle2 className="w-3 h-3" />
                      Texte extrait
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={() => onDelete(doc.id)}
            className="p-2 hover:bg-red-500/10 rounded-lg transition text-gray-400 hover:text-red-400"
            title="Supprimer"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
};
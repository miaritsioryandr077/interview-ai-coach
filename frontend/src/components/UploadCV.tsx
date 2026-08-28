import React, { useState, useRef } from 'react';
import { Upload, File, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface UploadCVProps {
  onUploadSuccess: () => void;
}

export const UploadCV: React.FC<UploadCVProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    
    // Validate PDF
    if (selected.type !== 'application/pdf' && !selected.name.toLowerCase().endsWith('.pdf')) {
      setError('Veuillez sélectionner un fichier PDF');
      setFile(null);
      return;
    }
    
    if (selected.size > 5 * 1024 * 1024) {
      setError('Le fichier ne doit pas dépasser 5MB');
      setFile(null);
      return;
    }
    
    setFile(selected);
    setError(null);
    setSuccess(false);
  };

const handleUpload = async () => {
  if (!file) return;
  
  setUploading(true);
  setError(null);
  setSuccess(false);
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    
    const response = await fetch('/api/v1/documents/upload/cv', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Upload failed');
    }
    
    await response.json();
    setSuccess(true);
    setFile(null);
    onUploadSuccess();
  } catch (err: any) {
    setError(err.message || 'Une erreur est survenue');
  } finally {
    setUploading(false);
  }
};
  const handleRemoveFile = () => {
    setFile(null);
    setError(null);
    setSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
      <h3 className="text-lg font-bold text-white flex items-center gap-2">
        <Upload className="w-5 h-5 text-brand-400" />
        Télécharger mon CV
      </h3>
      
      <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-brand-500/50 transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileSelect}
          className="hidden"
          id="cv-upload"
        />
        
        {!file && !success && (
          <div className="space-y-4">
            <File className="w-12 h-12 text-gray-500 mx-auto" />
            <p className="text-gray-400 text-sm">
              Glissez-déposez votre CV (PDF) ou
            </p>
            <label
              htmlFor="cv-upload"
              className="inline-block px-4 py-2 bg-brand-600/20 text-brand-400 rounded-lg font-semibold text-sm cursor-pointer hover:bg-brand-600/30 transition"
            >
              Parcourir...
            </label>
            <p className="text-xs text-gray-500">Maximum 5MB • Format PDF uniquement</p>
          </div>
        )}
        
        {file && !success && (
          <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
            <div className="flex items-center gap-3">
              <File className="w-8 h-8 text-brand-400" />
              <div className="text-left">
                <p className="text-white text-sm font-medium truncate max-w-[200px]">
                  {file.name}
                </p>
                <p className="text-xs text-gray-400">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
            <button
              onClick={handleRemoveFile}
              className="p-1.5 hover:bg-gray-700 rounded-lg transition"
            >
              <X className="w-5 h-5 text-gray-400 hover:text-red-400" />
            </button>
          </div>
        )}
        
        {success && (
          <div className="flex items-center gap-3 text-emerald-400 justify-center">
            <CheckCircle className="w-8 h-8" />
            <span className="font-medium">CV uploadé avec succès !</span>
          </div>
        )}
      </div>
      
      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 px-4 py-2 rounded-lg">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}
      
      {file && !success && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="w-full py-3 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Envoi en cours...
            </>
          ) : (
            'Envoyer mon CV'
          )}
        </button>
      )}
    </div>
  );
};
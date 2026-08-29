import { fetchApi } from '../lib/api';
import { Document, DocumentUploadResponse, DocumentType } from '../types/document';

export const documentService = {

  // Dans l'objet documentService, ajoutez en dessous de uploadCV :

  uploadJobOffer: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/documents/upload/job_offer', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Upload failed');
    }
    
    return response.json();
  },

  uploadCV: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Utiliser fetch directement mais avec le token
    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/documents/upload/cv', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        // Ne pas mettre 'Content-Type' car fetch le gère automatiquement avec FormData
      },
      body: formData,
    });

    
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Upload failed');
    }
    
    return response.json();
  },
  
  getMyDocuments: async (): Promise<Document[]> => {
    return fetchApi<Document[]>('/documents/');
  },
  
  deleteDocument: async (id: number): Promise<void> => {
    await fetchApi(`/documents/${id}`, { method: 'DELETE' });
  }
};


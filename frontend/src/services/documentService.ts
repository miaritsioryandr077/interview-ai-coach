import { fetchApi } from '../lib/api';
import { Document, DocumentUploadResponse, DocumentType } from '../types/document';

export const documentService = {
  uploadCV: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/v1/documents/upload/cv', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
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
    return fetchApi<Document[]>('/documents');
  },
  
  deleteDocument: async (id: number): Promise<void> => {
    await fetchApi(`/documents/${id}`, { method: 'DELETE' });
  }
};
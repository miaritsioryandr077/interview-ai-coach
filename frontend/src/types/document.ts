export enum DocumentType {
  CV = 'cv',
  JOB_OFFER = 'job_offer'
}

export interface Document {
  id: number;
  user_id: number;
  document_type: DocumentType;
  original_filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  extracted_text?: string;
}

export interface DocumentUploadResponse {
  id: number;
  original_filename: string;
  document_type: DocumentType;
  file_size: number;
  uploaded_at: string;
  message: string;
}
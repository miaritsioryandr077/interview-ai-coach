import { Document } from './document';

export interface Context {
  id: number;
  user_id: number;
  cv_id: number;
  job_id: number;
  notes?: string;
  created_at: string;
  cv?: Document;
  job?: Document;
}

export interface ContextCreate {
  cv_id: number;
  job_id: number;
  notes?: string;
}
import { Question } from './question';

export type SessionStatus = 'in_progress' | 'completed';

export interface InterviewResponse {
  id: number;
  session_id: number;
  question_id: number;
  text: string;
  created_at: string;
  /** Chemin serveur du fichier audio (réponse vocale), null si réponse textuelle. */
  answer_audio_path?: string | null;
}

export interface TranscriptionResult {
  question_id: number;
  text: string;
  response: InterviewResponse;
}

export interface InterviewSession {
  id: number;
  context_id: number;
  user_id: number;
  status: SessionStatus;
  started_at: string;
  ended_at: string | null;
  total_questions: number;
  questions: Question[];
  responses: InterviewResponse[];
  analysis?: any;
}

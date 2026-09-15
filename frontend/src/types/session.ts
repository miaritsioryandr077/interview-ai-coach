import { Question } from './question';

export type SessionStatus = 'in_progress' | 'completed';

export interface InterviewResponse {
  id: number;
  session_id: number;
  question_id: number;
  text: string;
  created_at: string;
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
}

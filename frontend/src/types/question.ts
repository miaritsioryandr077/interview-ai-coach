export interface Question {
  id: number;
  context_id: number;
  text: string;
  category: string;
  difficulty: string;
  order_index: number;
  expected_duration_seconds: number;
  created_at: string;
}
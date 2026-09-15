import { fetchApi } from "../lib/api";
import { InterviewResponse, InterviewSession } from "../types/session";

export const sessionService = {
  startSession: async (contextId: number): Promise<InterviewSession> => {
    return fetchApi<InterviewSession>(`/contexts/${contextId}/sessions`, {
      method: "POST",
    });
  },

  getSession: async (sessionId: number): Promise<InterviewSession> => {
    return fetchApi<InterviewSession>(`/sessions/${sessionId}`);
  },

  getMySessions: async (): Promise<InterviewSession[]> => {
    return fetchApi<InterviewSession[]>("/sessions/");
  },

  saveResponse: async (
    sessionId: number,
    questionId: number,
    text: string,
  ): Promise<InterviewResponse> => {
    return fetchApi<InterviewResponse>(`/sessions/${sessionId}/responses`, {
      method: "POST",
      body: JSON.stringify({ question_id: questionId, text }),
    });
  },

  completeSession: async (sessionId: number): Promise<InterviewSession> => {
    return fetchApi<InterviewSession>(`/sessions/${sessionId}/complete`, {
      method: "POST",
    });
  },
};

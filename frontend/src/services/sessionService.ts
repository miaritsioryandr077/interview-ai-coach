import { fetchApi } from "../lib/api";
import {
  InterviewResponse,
  InterviewSession,
  TranscriptionResult,
} from "../types/session";

/**
 * Envoi d'un fichier audio : pas de Content-Type JSON (le navigateur doit
 * générer lui-même le multipart avec sa boundary).
 */
async function uploadAudio(
  sessionId: number,
  questionId: number,
  blob: Blob,
): Promise<InterviewResponse> {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  const extension = blob.type.includes("ogg")
    ? "ogg"
    : blob.type.includes("wav")
      ? "wav"
      : blob.type.includes("mpeg")
        ? "mp3"
        : "webm";
  formData.append("file", blob, `answer.${extension}`);

  const response = await fetch(
    `/api/v1/sessions/${sessionId}/responses/${questionId}/audio`,
    {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    },
  );
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(
      data.detail || `Échec de l'envoi de l'audio (${response.status})`,
    );
  }
  return data as InterviewResponse;
}

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

  uploadResponseAudio: uploadAudio,

  transcribeResponse: async (
    sessionId: number,
    questionId: number,
  ): Promise<TranscriptionResult> => {
    return fetchApi<TranscriptionResult>(
      `/sessions/${sessionId}/responses/${questionId}/transcribe`,
      { method: "POST" },
    );
  },

  completeSession: async (sessionId: number): Promise<InterviewSession> => {
    return fetchApi<InterviewSession>(`/sessions/${sessionId}/complete`, {
      method: "POST",
    });
  },

  analyzeSession: async (sessionId: number): Promise<any> => {
    return fetchApi<any>(`/sessions/${sessionId}/analyze`, {
      method: "POST",
    });
  },

  getAnalysis: async (sessionId: number): Promise<any> => {
    return fetchApi<any>(`/sessions/${sessionId}/analysis`);
  },
};

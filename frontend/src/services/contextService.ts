import { fetchApi } from '../lib/api';
import { Context, ContextCreate } from '../types/context';
import { Question } from '../types/question';

export const contextService = {
  createContext: async (data: ContextCreate): Promise<Context> => {
    return fetchApi<Context>('/contexts/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  getMyContexts: async (): Promise<Context[]> => {
    return fetchApi<Context[]>('/contexts/');
  },
  generateQuestions: async (contextId: number): Promise<Question[]> => {
    return fetchApi<Question[]>(`/contexts/${contextId}/generate-questions`, {
      method: 'POST'
    });
  },
  getContextQuestions: async (contextId: number): Promise<Question[]> => {
    return fetchApi<Question[]>(`/contexts/${contextId}/questions`);
  }
};
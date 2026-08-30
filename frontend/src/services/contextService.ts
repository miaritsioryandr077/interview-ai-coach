import { fetchApi } from '../lib/api';
import { Context, ContextCreate } from '../types/context';

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
};
import { fetchApi } from '../lib/api';

export const progressService = {
  getProgress: async (): Promise<any> => {
    return fetchApi<any>('/progress');
  },
  getPreparationProgress: async (preparationId: number): Promise<any> => {
    return fetchApi<any>(`/preparations/${preparationId}/progress`);
  },
};
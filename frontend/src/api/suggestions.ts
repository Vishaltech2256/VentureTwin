import client from './client';
import { AISuggestionResponse, AISuggestionGenerationResponse } from '../types';

export const aiSuggestionApi = {
  /** Generate suggestions based on the startup's latest prediction */
  generate: async (startupId: number): Promise<AISuggestionGenerationResponse> => {
    const res = await client.post<AISuggestionGenerationResponse>(`/ai-suggestions/generate/${startupId}`);
    return res.data;
  },

  /** List suggestions for a startup, newest first */
  list: async (startupId: number): Promise<AISuggestionResponse[]> => {
    const res = await client.get<AISuggestionResponse[]>(`/ai-suggestions/${startupId}`);
    return res.data;
  },

  /** Get a single suggestion by its ID */
  getDetail: async (suggestionId: number): Promise<AISuggestionResponse> => {
    const res = await client.get<AISuggestionResponse>(`/ai-suggestions/detail/${suggestionId}`);
    return res.data;
  },

  /** Delete a single suggestion permanently */
  delete: async (suggestionId: number): Promise<{ message: string }> => {
    const res = await client.delete<{ message: string }>(`/ai-suggestions/${suggestionId}`);
    return res.data;
  },
};

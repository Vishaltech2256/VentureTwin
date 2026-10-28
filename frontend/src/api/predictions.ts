import client from './client';
import { PredictionResponse } from '../types';

export const predictionApi = {
  /** Trigger a rule-based prediction run for a startup */
  run: async (startupId: number): Promise<PredictionResponse> => {
    const res = await client.post<PredictionResponse>(`/predictions/run/${startupId}`);
    return res.data;
  },

  /** Get all predictions for a startup (historical list) */
  list: async (startupId: number): Promise<PredictionResponse[]> => {
    const res = await client.get<PredictionResponse[]>(`/predictions/${startupId}`);
    return res.data;
  },

  /** Get the latest prediction for a startup */
  getLatest: async (startupId: number): Promise<PredictionResponse> => {
    const res = await client.get<PredictionResponse>(`/predictions/${startupId}/latest`);
    return res.data;
  },
};

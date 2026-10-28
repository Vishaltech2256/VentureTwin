import client from './client';
import { DashboardResponse } from '../types';

export const dashboardApi = {
  /** Get overview metrics, recent startups, and predictions */
  get: async (): Promise<DashboardResponse> => {
    const res = await client.get<DashboardResponse>('/dashboard/');
    return res.data;
  },
};

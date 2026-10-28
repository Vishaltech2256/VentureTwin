import client from './client';
import {
  StartupProfileCreate,
  StartupProfileUpdate,
  StartupProfileResponse,
  FinancialInformationCreate,
  FinancialInformationResponse,
  TeamInformationCreate,
  TeamInformationResponse,
  BusinessLocationCreate,
  BusinessLocationResponse,
  LandDetailsCreate,
  LandDetailsResponse,
  StartupFullData,
  PredictionResponse,
  AISuggestionResponse,
  ReportResponse,
} from '../types';

export const startupApi = {
  create: async (data: StartupProfileCreate): Promise<StartupProfileResponse> => {
    const res = await client.post<StartupProfileResponse>('/startup-profile/', data);
    return res.data;
  },

  list: async (): Promise<StartupProfileResponse[]> => {
    const res = await client.get<StartupProfileResponse[]>('/startup-profile/');
    return res.data;
  },

  get: async (startupId: number): Promise<StartupProfileResponse> => {
    const res = await client.get<StartupProfileResponse>(`/startup-profile/${startupId}`);
    return res.data;
  },

  update: async (startupId: number, data: StartupProfileUpdate): Promise<StartupProfileResponse> => {
    const res = await client.patch<StartupProfileResponse>(`/startup-profile/${startupId}`, data);
    return res.data;
  },

  delete: async (startupId: number): Promise<{ message: string }> => {
    const res = await client.delete<{ message: string }>(`/startup-profile/${startupId}`);
    return res.data;
  },

  /**
   * Fetches full aggregate data for a startup including all optional subresources.
   * Gracefully returns null for any subresource that has not yet been populated.
   */
  getFull: async (startupId: number): Promise<StartupFullData> => {
    const profile = await startupApi.get(startupId);

    const [
      financialResult,
      teamResult,
      locationResult,
      landResult,
      predResult,
      suggResult,
      repResult,
    ] = await Promise.allSettled([
      financialApi.get(startupId),
      teamApi.get(startupId),
      locationApi.get(startupId),
      landApi.get(startupId),
      client.get<PredictionResponse>(`/predictions/${startupId}/latest`),
      client.get<AISuggestionResponse[]>(`/ai-suggestions/${startupId}`),
      client.get<ReportResponse[]>(`/reports/startup/${startupId}`),
    ]);


    return {
      profile,
      financial: financialResult.status === 'fulfilled' ? financialResult.value : null,
      team: teamResult.status === 'fulfilled' ? teamResult.value : null,
      location: locationResult.status === 'fulfilled' ? locationResult.value : null,
      land: landResult.status === 'fulfilled' ? landResult.value : null,
      latestPrediction:
        predResult.status === 'fulfilled' ? predResult.value.data : null,
      suggestions:
        suggResult.status === 'fulfilled' ? suggResult.value.data : [],
      reports:
        repResult.status === 'fulfilled' ? repResult.value.data : [],
    };
  },
};

export const financialApi = {
  upsert: async (startupId: number, data: FinancialInformationCreate): Promise<FinancialInformationResponse> => {
    const res = await client.put<FinancialInformationResponse>(`/financial-information/${startupId}`, data);
    return res.data;
  },

  get: async (startupId: number): Promise<FinancialInformationResponse> => {
    const res = await client.get<FinancialInformationResponse>(`/financial-information/${startupId}`);
    return res.data;
  },
};

export const teamApi = {
  upsert: async (startupId: number, data: TeamInformationCreate): Promise<TeamInformationResponse> => {
    const res = await client.put<TeamInformationResponse>(`/team-information/${startupId}`, data);
    return res.data;
  },

  get: async (startupId: number): Promise<TeamInformationResponse> => {
    const res = await client.get<TeamInformationResponse>(`/team-information/${startupId}`);
    return res.data;
  },
};

export const locationApi = {
  upsert: async (startupId: number, data: BusinessLocationCreate): Promise<BusinessLocationResponse> => {
    const res = await client.put<BusinessLocationResponse>(`/business-location/${startupId}`, data);
    return res.data;
  },

  get: async (startupId: number): Promise<BusinessLocationResponse> => {
    const res = await client.get<BusinessLocationResponse>(`/business-location/${startupId}`);
    return res.data;
  },
};

export const landApi = {
  upsert: async (startupId: number, data: LandDetailsCreate): Promise<LandDetailsResponse> => {
    const res = await client.put<LandDetailsResponse>(`/land-details/${startupId}`, data);
    return res.data;
  },

  get: async (startupId: number): Promise<LandDetailsResponse> => {
    const res = await client.get<LandDetailsResponse>(`/land-details/${startupId}`);
    return res.data;
  },
};

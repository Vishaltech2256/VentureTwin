import client from './client';
import { ReportResponse } from '../types';

export const reportApi = {
  /** Generate a new ReportLab PDF report for the startup */
  generate: async (startupId: number): Promise<ReportResponse> => {
    const res = await client.post<ReportResponse>(`/reports/generate/${startupId}`);
    return res.data;
  },

  /** List generated reports for a startup */
  list: async (startupId: number): Promise<ReportResponse[]> => {
    const res = await client.get<ReportResponse[]>(`/reports/startup/${startupId}`);
    return res.data;
  },


  /**
   * Securely download a PDF report using authenticated client blob retrieval.
   * This ensures the Bearer token header is transmitted so the backend doesn't 401.
   */
  downloadPdf: async (reportId: number, filename = 'venturetwin_report.pdf'): Promise<void> => {
    const res = await client.get(`/reports/download/${reportId}`, {
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'application/pdf' });
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  },
};

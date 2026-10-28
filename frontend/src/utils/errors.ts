import { AxiosError } from 'axios';

export interface NormalizedError {
  message: string;
  fieldErrors: Record<string, string>;
  status?: number;
}

export function normalizeError(error: unknown): NormalizedError {
  if (typeof error === 'string') {
    return { message: error, fieldErrors: {} };
  }

  const axiosError = error as AxiosError<{ detail?: unknown; message?: string }>;

  if (!axiosError || !axiosError.isAxiosError) {
    if (error instanceof Error) {
      return { message: error.message, fieldErrors: {} };
    }
    return { message: 'An unexpected error occurred. Please try again.', fieldErrors: {} };
  }

  const status = axiosError.response?.status;
  const data = axiosError.response?.data;

  // Network / server offline
  if (!axiosError.response) {
    return {
      message: 'Unable to reach the VentureTwin backend server. Please verify the backend is running.',
      fieldErrors: {},
      status: 0,
    };
  }

  const fieldErrors: Record<string, string> = {};
  let message = 'An error occurred while processing your request.';

  if (data?.detail) {
    if (typeof data.detail === 'string') {
      message = data.detail;
    } else if (Array.isArray(data.detail)) {
      // Pydantic validation error list
      const messages: string[] = [];
      data.detail.forEach((err: { loc?: (string | number)[]; msg?: string }) => {
        if (err.loc && err.loc.length > 0) {
          const field = String(err.loc[err.loc.length - 1]);
          if (err.msg) {
            fieldErrors[field] = err.msg;
            messages.push(`${field}: ${err.msg}`);
          }
        } else if (err.msg) {
          messages.push(err.msg);
        }
      });
      if (messages.length > 0) {
        message = messages.join('; ');
      }
    }
  } else if (data?.message) {
    message = data.message;
  } else if (status === 401) {
    message = 'Authentication required or session expired. Please sign in again.';
  } else if (status === 403) {
    message = 'Access denied. You do not have permission to access this resource.';
  } else if (status === 404) {
    message = 'The requested resource was not found.';
  } else if (status === 500) {
    message = 'A server error occurred on the backend. Please check server logs.';
  }

  return { message, fieldErrors, status };
}

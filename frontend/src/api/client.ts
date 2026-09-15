import axios from 'axios';
import type { AnalysisResponse, FeedbackRequest } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const analyzeText = async (text: string, context?: string): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/api/analyze/text', {
    text,
    context: context || '',
  });
  return response.data;
};

export const analyzeImage = async (file: File, context?: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (context) {
    formData.append('context', context);
  }

  const response = await api.post<AnalysisResponse>('/api/analyze/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeAudio = async (file: File, context?: string): Promise<AnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  if (context) {
    formData.append('context', context);
  }

  const response = await api.post<AnalysisResponse>('/api/analyze/audio', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeUrl = async (url: string, context?: string): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/api/analyze/url', {
    url,
    context: context || '',
  });
  return response.data;
};

export const submitFeedback = async (feedback: FeedbackRequest): Promise<{ status: string; message: string }> => {
  const response = await api.post<{ status: string; message: string }>('/api/feedback', feedback);
  return response.data;
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health');
    return response.data.status === 'healthy';
  } catch {
    return false;
  }
};

import axios from 'axios';
import { ProcessingRequest } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for image processing
});

export const processImage = async (
  file: File, 
  request: ProcessingRequest
): Promise<string> => {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('style', request.style);
  
  if (request.customSettings) {
    formData.append('custom_settings', JSON.stringify(request.customSettings));
  }

  const response = await api.post('/api/v1/process-image/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
  });

  // Convert blob to URL for display
  const imageUrl = URL.createObjectURL(response.data);
  return imageUrl;
};

export const processImageAsync = async (
  file: File, 
  request: ProcessingRequest
): Promise<{ job_id: string; status: string }> => {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('style', request.style);
  
  if (request.customSettings) {
    formData.append('custom_settings', JSON.stringify(request.customSettings));
  }

  const response = await api.post('/api/v1/process-image-async/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const getJobStatus = async (jobId: string) => {
  const response = await api.get(`/api/v1/job-status/${jobId}`);
  return response.data;
};

export const getAvailableStyles = async (): Promise<string[]> => {
  const response = await api.get('/api/v1/styles/');
  return response.data.styles;
};

export const getStylePreset = async (styleName: string) => {
  const response = await api.get(`/api/v1/styles/${styleName}/`);
  return response.data;
};
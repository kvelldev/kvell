/**
 * Health Repository
 * 
 * API communication layer for health check operations.
 */

import type { HealthMessage } from '@/domain/model/health';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const saveHealthMessage = async (message: string): Promise<HealthMessage> => {
  const response = await fetch(`${API_BASE_URL}/api/health/echo`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(`Failed to save message: ${response.statusText}`);
  }

  const data = await response.json();
  
  return {
    id: data.id,
    message: data.message,
    createdAt: data.created_at,
  };
};

export const getLatestHealthMessage = async (): Promise<HealthMessage | null> => {
  const response = await fetch(`${API_BASE_URL}/api/health/latest`);

  if (!response.ok) {
    throw new Error(`Failed to get latest message: ${response.statusText}`);
  }

  const data = await response.json();
  
  if (!data) {
    return null;
  }

  return {
    id: data.id,
    message: data.message,
    createdAt: data.created_at,
  };
};

/**
 * Health Check UseCase Hook
 * 
 * Custom hook for health check operations.
 */

import { useState } from 'react';
import type { HealthMessage } from '@/domain/model/health';
import { saveHealthMessage, getLatestHealthMessage } from '@/adapter/repository/healthRepository';

interface UseHealthCheckReturn {
  message: HealthMessage | null;
  isLoading: boolean;
  error: Error | null;
  saveMessage: (text: string) => Promise<void>;
  fetchLatest: () => Promise<void>;
}

export const useHealthCheck = (): UseHealthCheckReturn => {
  const [message, setMessage] = useState<HealthMessage | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const saveMessage = async (text: string): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const savedMessage = await saveHealthMessage(text);
      setMessage(savedMessage);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLatest = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const latestMessage = await getLatestHealthMessage();
      setMessage(latestMessage);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setIsLoading(false);
    }
  };

  return {
    message,
    isLoading,
    error,
    saveMessage,
    fetchLatest,
  };
};

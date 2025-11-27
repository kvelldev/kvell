/**
 * Health Repository Implementation
 *
 * Adapter layer implementation of IHealthRepository.
 * Handles API communication for health check operations.
 */

import type { HealthMessage } from "@/domain/model/health";
import type { IHealthRepository } from "@/domain/repository/healthRepository";

/**
 * API response type for health message endpoints
 */
interface HealthMessageApiResponse {
  id: string;
  message: string;
  created_at: string;
}

/**
 * Type-safe environment variable access
 * @returns The API base URL from environment or default value
 */
const getApiBaseUrl = (): string => {
  const env = import.meta.env as { VITE_API_BASE_URL?: string };
  return env.VITE_API_BASE_URL ?? "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Health Repository implementation
 */
class HealthRepositoryImpl implements IHealthRepository {
  async saveMessage(message: string): Promise<HealthMessage> {
    const response = await fetch(`${API_BASE_URL}/api/health/echo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Failed to save message: ${response.statusText}`);
    }

    const data = (await response.json()) as HealthMessageApiResponse;

    return {
      id: data.id,
      message: data.message,
      createdAt: data.created_at,
    };
  }

  async getLatest(): Promise<HealthMessage | null> {
    const response = await fetch(`${API_BASE_URL}/api/health/latest`);

    if (!response.ok) {
      throw new Error(`Failed to get latest message: ${response.statusText}`);
    }

    const data = (await response.json()) as HealthMessageApiResponse | null;

    if (!data) {
      return null;
    }

    return {
      id: data.id,
      message: data.message,
      createdAt: data.created_at,
    };
  }
}

/**
 * Singleton instance of Health Repository
 */
export const healthRepository: IHealthRepository = new HealthRepositoryImpl();

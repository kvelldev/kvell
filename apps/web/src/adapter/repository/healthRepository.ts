/**
 * Health Repository Implementation
 *
 * Adapter layer implementation of IHealthRepository.
 * Handles API communication for health check operations using apiClient.
 */

import type { HealthMessage } from "@/domain/model/health";
import type { IHealthRepository } from "@/domain/repository/healthRepository";
import { apiClient } from "@/adapter/apiClient";

/**
 * API response type for health message endpoints
 */
interface HealthMessageApiResponse {
  id: string;
  message: string;
  created_at: string;
}

/**
 * Health Repository implementation
 */
class HealthRepositoryImpl implements IHealthRepository {
  async saveMessage(message: string): Promise<HealthMessage> {
    const data = await apiClient<HealthMessageApiResponse>("/api/health/echo", {
      method: "POST",
      body: JSON.stringify({ message }),
    });

    return {
      id: data.id,
      message: data.message,
      createdAt: data.created_at,
    };
  }

  async getLatest(): Promise<HealthMessage | null> {
    const data = await apiClient<HealthMessageApiResponse | null>(
      "/api/health/latest",
    );

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

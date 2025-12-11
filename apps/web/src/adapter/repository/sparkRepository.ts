/**
 * Spark Repository Implementation
 *
 * Adapter layer implementation of ISparkRepository.
 * Handles API communication for spark operations using apiClient.
 */

import type { PostSparkRequest, Spark } from "@/domain/model/spark";
import type { ISparkRepository } from "@/domain/repository/sparkRepository";
import { apiClient } from "@/adapter/apiClient";

/**
 * API response type for spark endpoints (snake_case from backend)
 */
interface SparkApiResponse {
  id: string;
  content: string;
  created_at: string;
  decay_at: string;
}

/**
 * Spark Repository implementation
 */
class SparkRepositoryImpl implements ISparkRepository {
  async postSpark(request: PostSparkRequest): Promise<Spark> {
    const data = await apiClient<SparkApiResponse>("/api/sparks", {
      method: "POST",
      body: JSON.stringify({ content: request.content }),
    });

    // Transform snake_case API response to camelCase domain model
    return {
      id: data.id,
      content: data.content,
      createdAt: data.created_at,
      decayAt: data.decay_at,
    };
  }
}

/**
 * Singleton instance of Spark Repository
 */
export const sparkRepository: ISparkRepository = new SparkRepositoryImpl();

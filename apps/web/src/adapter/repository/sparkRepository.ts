/**
 * Spark Repository Implementation
 *
 * Adapter layer implementation of ISparkRepository.
 * Handles API communication for spark operations using apiClient.
 */

import type {
  AddFuelRequest,
  PostSparkRequest,
  Spark,
} from "@/domain/model/spark";
import type {
  ISparkRepository,
  PostReplyRequest,
} from "@/domain/repository/sparkRepository";
import { apiClient } from "@/adapter/apiClient";

/**
 * API response type for spark endpoints (snake_case from backend)
 */
interface SparkApiResponse {
  id: string;
  content: string;
  user_hash: string;
  created_at: string;
  decay_at: string;
  parent_bonfire_id?: string;
}

/**
 * Spark Repository implementation
 */
class SparkRepositoryImpl implements ISparkRepository {
  async postSpark(request: PostSparkRequest): Promise<Spark> {
    const data = await apiClient<SparkApiResponse>("/api/sparks", {
      method: "POST",
      body: JSON.stringify({
        content: request.content,
        field_id: request.fieldId,
      }),
    });

    // Transform snake_case API response to camelCase domain model
    return {
      id: data.id,
      content: data.content,
      userHash: data.user_hash,
      createdAt: data.created_at,
      decayAt: data.decay_at,
    };
  }

  async postReply(request: PostReplyRequest): Promise<Spark> {
    const data = await apiClient<SparkApiResponse>("/api/sparks", {
      method: "POST",
      body: JSON.stringify({
        content: request.content,
        parent_bonfire_id: request.parentBonfireId,
        field_id: request.fieldId,
      }),
    });

    // Transform snake_case API response to camelCase domain model
    return {
      id: data.id,
      content: data.content,
      userHash: data.user_hash,
      createdAt: data.created_at,
      decayAt: data.decay_at,
      parentBonfireId: data.parent_bonfire_id,
    };
  }

  async addFuel(request: AddFuelRequest): Promise<void> {
    // POST /api/sparks/{sparkId}/fuel
    // The API returns 204 No Content to hide fuel count from users
    await apiClient<null>(`/api/sparks/${request.sparkId}/fuel`, {
      method: "POST",
    });
  }
}

/**
 * Singleton instance of Spark Repository
 */
export const sparkRepository: ISparkRepository = new SparkRepositoryImpl();

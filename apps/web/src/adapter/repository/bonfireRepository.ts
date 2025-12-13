/**
 * Bonfire Repository Interface and Implementation
 */

import type { BonfireList } from "@/domain/model/bonfire";
import { apiClient } from "@/adapter/apiClient";
import type { IBonfireRepository } from "@/domain/repository/bonfireRepository";

/**
 * API response type for bonfire endpoints (snake_case from backend)
 */
interface BonfireApiResponse {
  id: string;
  spark_id: string;
  content: string;
  unique_user_count: number;
  heat_score: number;
  created_at: string;
  decay_at: string;
}

interface BonfireListApiResponse {
  bonfires: BonfireApiResponse[];
  count: number;
}

interface MessageResponse {
  message: string;
}

class BonfireRepositoryImpl implements IBonfireRepository {
  async getActiveBonfires(): Promise<BonfireList> {
    const data = await apiClient<BonfireListApiResponse>("/api/bonfires", {
      method: "GET",
    });

    return {
      bonfires: data.bonfires.map((b) => ({
        id: b.id,
        sparkId: b.spark_id,
        content: b.content,
        uniqueUserCount: b.unique_user_count,
        heatScore: b.heat_score,
        createdAt: b.created_at,
        decayAt: b.decay_at,
      })),
      count: data.count,
    };
  }

  async seedDemoBonfires(): Promise<string> {
    const data = await apiClient<MessageResponse>("/api/bonfires/seed", {
      method: "POST",
    });
    return data.message;
  }

  async deleteAllBonfires(): Promise<string> {
    const data = await apiClient<MessageResponse>("/api/bonfires", {
      method: "DELETE",
    });
    return data.message;
  }
}

export const bonfireRepository: IBonfireRepository =
  new BonfireRepositoryImpl();

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
  field_id: string;
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

class BonfireRepositoryImpl implements IBonfireRepository {
  async getActiveBonfires(fieldId?: string): Promise<BonfireList> {
    const searchParameters = new URLSearchParams();
    if (fieldId) {
      searchParameters.append("field_id", fieldId);
    }
    const query = searchParameters.toString();
    const url = `/api/bonfires${query ? `?${query}` : ""}`;

    const data = await apiClient<BonfireListApiResponse>(url, {
      method: "GET",
    });

    return {
      bonfires: data.bonfires.map((b) => ({
        id: b.id,
        sparkId: b.spark_id,
        fieldId: b.field_id,
        content: b.content,
        uniqueUserCount: b.unique_user_count,
        heatScore: b.heat_score,
        createdAt: b.created_at,
        decayAt: b.decay_at,
      })),
      count: data.count,
    };
  }
}

export const bonfireRepository: IBonfireRepository =
  new BonfireRepositoryImpl();

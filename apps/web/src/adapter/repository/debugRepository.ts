/**
 * Debug Repository
 *
 * Provides debug/demo operations (seed, cleanup).
 */

import { apiClient } from "@/adapter/apiClient";

interface MessageResponse {
  message: string;
}

export const debugRepository = {
  async seedBonfires(): Promise<string> {
    const data = await apiClient<MessageResponse>("/api/debug/seed", {
      method: "POST",
    });
    return data.message;
  },

  async cleanupBonfires(): Promise<string> {
    const data = await apiClient<MessageResponse>("/api/debug/cleanup", {
      method: "DELETE",
    });
    return data.message;
  },
};

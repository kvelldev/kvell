// fetchをラップし、共通のヘッダー処理とAppErrorへの変換を行う
import AppError from "@/domain/appError";
import type { InternalStatusCodes } from "@/domain/constants";

const BASE_URL: string = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

export const apiClient = async <T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> => {
  try {
    const headers = new Headers(options?.headers);
    headers.set("Content-Type", "application/json");

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // ステータスコードに応じたエラーハンドリング(簡易実装)
      throw new AppError(
        response.status as InternalStatusCodes,
        `API Error: ${response.statusText}`,
      );
    }

    // 204 No Contentの場合はnullを返す等の処理もここに記述
    if (response.status === 204) return null as T;

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof AppError) throw error;
    throw new AppError(500, "Network Error", { cause: error as Error });
  }
};

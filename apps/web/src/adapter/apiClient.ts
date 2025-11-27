// fetchをラップし、共通のヘッダー処理とAppErrorへの変換を行う
import AppError from "@/domain/appError";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = async <T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> => {
  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      headers: { "Content-Type": "application/json", ...options?.headers },
      ...options,
    });

    if (!res.ok) {
      // ステータスコードに応じたエラーハンドリング(簡易実装)
      throw new AppError(res.status as any, `API Error: ${res.statusText}`);
    }

    // 204 No Contentの場合はnullを返す等の処理もここに記述
    if (res.status === 204) return null as T;

    return res.json();
  } catch (error) {
    if (error instanceof AppError) throw error;
    throw new AppError(500, "Network Error", error as Error);
  }
};

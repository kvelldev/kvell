import { useState, useCallback, useEffect, useRef } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";

export type ConnectionStatus =
  | { type: "connected" }
  | { type: "disconnected" }
  | {
      type: "reconnecting";
      attempt: number;
      maxAttempts: number;
      nextRetryDelayMs: number;
    }
  | { type: "error"; reason: string };

const MAX_RETRIES = 3;
const BASE_DELAY = 1000;
const MAX_DELAY = 10000;
const CONNECTION_TIMEOUT_MS = 1000;

export const useResilientConnection = (
  repository: ITimelineRepository,
  onMessage: (event: any) => void,
) => {
  // ★重要: ロジック制御用のカウントは Ref で管理（即時反映させるため）
  const retryCountRef = useRef(0);
  // UI反映用のカウント（Refと同期させる）
  const [retryCount, setRetryCount] = useState(0);
  const [nextDelay, setNextDelay] = useState(0);

  const calculateBackoff = useCallback((attempt: number) => {
    const delay = Math.min(BASE_DELAY * Math.pow(2, attempt), MAX_DELAY);
    const jitter = delay * (0.1 + Math.random() * 0.2);
    return delay + jitter;
  }, []);

  const { lastMessage, readyState, getWebSocket } = useWebSocket(
    repository.connectionUrl,
    {
      shouldReconnect: () => {
        // ★修正点1: Refの最新値を参照する
        // ★修正点2: '<=' に変更。
        // count=3 (3回失敗) のときも true を返し、3回目のリトライ(Wait->Connect)を実行させる。
        // count=4 (3回目のリトライ失敗) になったら false で止める。
        return retryCountRef.current <= MAX_RETRIES;
      },
      reconnectInterval: (attemptNumber) => {
        const delay = calculateBackoff(attemptNumber);
        setNextDelay(delay);
        return delay;
      },
      onOpen: () => {
        retryCountRef.current = 0;
        setRetryCount(0);
        setNextDelay(0);
      },
      onClose: () => {
        // 切断時にカウントアップ
        retryCountRef.current += 1;
        setRetryCount(retryCountRef.current); // UI更新
      },
      onError: (event) => {
        console.error("WebSocket error", event);
      },
    },
  );

  // 接続タイムアウト（5秒で諦めて次へ）
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;

    if (readyState === ReadyState.CONNECTING) {
      timeoutId = setTimeout(() => {
        const socket = getWebSocket();
        if (socket) {
          socket.close(); // onClose を発火させる
        }
      }, CONNECTION_TIMEOUT_MS);
    }

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [readyState, getWebSocket]);

  // メッセージ受信
  useEffect(() => {
    if (lastMessage) {
      const event = repository.parseMessage(lastMessage.data);
      if (event) {
        onMessage(event);
      }
    }
  }, [lastMessage, repository, onMessage]);

  // ステータス変換
  const getConnectionStatus = (): ConnectionStatus => {
    if (readyState === ReadyState.OPEN) {
      return { type: "connected" };
    }

    const currentCount = retryCount; // Stateの値を使用

    // エラー判定: 4回失敗 (3回目のリトライ失敗) したらエラー
    if (currentCount > MAX_RETRIES) {
      return { type: "error", reason: "Max retries exceeded" };
    }

    // 再接続中: 1回以上失敗しており、まだ上限(4回)に達していない
    // count=1 (1/3), count=2 (2/3), count=3 (3/3)
    if (currentCount > 0) {
      return {
        type: "reconnecting",
        attempt: currentCount,
        maxAttempts: MAX_RETRIES,
        nextRetryDelayMs: nextDelay,
      };
    }

    return { type: "disconnected" };
  };

  return getConnectionStatus();
};

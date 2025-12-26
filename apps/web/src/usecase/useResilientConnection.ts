import { useState, useCallback, useEffect, useRef } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";

/**
 *
 */
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
const MAX_DELAY = 10_000;
const CONNECTION_TIMEOUT_MS = 2000;

export const useResilientWebSocket = <T>(
  url: string,
  parseMessage: (data: unknown) => T | null,
  onMessage: (event: T) => void,
) => {
  // ★重要: ロジック制御用のカウントは Ref で管理（即時反映させるため）
  const retryCountRef = useRef(0);
  // UI反映用のカウント（Refと同期させる）
  const [retryCount, setRetryCount] = useState(0);
  const [nextDelay, setNextDelay] = useState(0);

  // 強制再接続用のキー（Long Sleep復帰時に更新してSocketを作り直す）
  const [connectKey, setConnectKey] = useState(0);
  const hiddenAtRef = useRef<number | null>(null);

  // URL変更時（Room切り替え等）に状態をリセット
  useEffect(() => {
    retryCountRef.current = 0;
    setRetryCount(0);
    setNextDelay(0);
    setConnectKey(0);
    hiddenAtRef.current = null;
  }, [url]);

  // Visibility Handling (Background Tab Logic)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        hiddenAtRef.current = Date.now();
      } else {
        if (hiddenAtRef.current) {
          const duration = Date.now() - hiddenAtRef.current;
          // 60秒以上のバックグラウンド滞在で強制再接続
          // Long Sleep: Force Reconnection (Zombie対策)
          if (duration > 60_000) {
            setConnectKey((previous) => previous + 1);
          }
          hiddenAtRef.current = null;
        }
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  const calculateBackoff = useCallback((attempt: number) => {
    const delay = Math.min(BASE_DELAY * Math.pow(2, attempt), MAX_DELAY);
    const jitter = delay * (0.1 + Math.random() * 0.2);
    return delay + jitter;
  }, []);

  // URLにキーを付与して変更を検知させる
  // url がクエリパラメータを含んでいる可能性も考慮
  const connectionUrl = `${url}${url.includes("?") ? "&" : "?"}_r=${String(connectKey)}`;

  const { lastMessage, readyState, getWebSocket } = useWebSocket(
    connectionUrl,
    {
      shouldReconnect: () => {
        // count=3 (3回失敗) のときも true を返し、3回目のリトライ(Wait->Connect)を実行させる。
        // count=4 (3回目のリトライ失敗) になったら false で止める。
        return retryCountRef.current <= MAX_RETRIES;
      },
      reconnectInterval: (attemptNumber: number) => {
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
    let timeoutId: ReturnType<typeof setTimeout>;

    if (readyState === ReadyState.CONNECTING) {
      timeoutId = setTimeout(() => {
        const socket = getWebSocket();
        // ★修正: まだ繋がっていない(CONNECTING)場合のみ切断する
        if (socket?.readyState === 0) {
          // 0 is WebSocket.CONNECTING
          socket.close(); // onClose を発火させる
        }
      }, CONNECTION_TIMEOUT_MS);
    }

    return () => {
      // safe cleanup
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [readyState, getWebSocket]);

  // メッセージ受信
  useEffect(() => {
    if (lastMessage) {
      const event = parseMessage(lastMessage.data);
      if (event) {
        onMessage(event);
      }
    }
  }, [lastMessage, parseMessage, onMessage]);

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

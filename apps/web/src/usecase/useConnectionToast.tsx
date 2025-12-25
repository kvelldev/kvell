import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { Wifi, WifiOff } from "lucide-react"; // Loader2は不要になります
import type { ConnectionStatus } from "./useTimelineStream";

export const useConnectionToast = (status: ConnectionStatus) => {
  const toastIdRef = useRef<string | number>("connection-status");

  const [isOnline, setIsOnline] = useState(navigator.onLine);
  // Reconnecting状態のDebounce用
  const [debouncedReconnecting, setDebouncedReconnecting] = useState(false);

  // Network Status Monitoring
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
    };
    const handleOffline = () => {
      setIsOnline(false);
    };
    globalThis.addEventListener("online", handleOnline);
    globalThis.addEventListener("offline", handleOffline);
    return () => {
      globalThis.removeEventListener("online", handleOnline);
      globalThis.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Debounce Reconnecting Status
  // 瞬断でToastが出ないように、2秒以上Reconnectingが続いた場合のみフラグを立てる
  useEffect(() => {
    if (status.type === "reconnecting") {
      const timer = setTimeout(() => {
        setDebouncedReconnecting(true);
      }, 2000);
      return () => {
        clearTimeout(timer);
      };
    } else {
      setDebouncedReconnecting(false);
    }
  }, [status.type]);

  const { type } = status;
  const attempt = status.type === "reconnecting" ? status.attempt : 0;
  const maxAttempts = status.type === "reconnecting" ? status.maxAttempts : 0;

  useEffect(() => {
    // 1. Offline Event (Highest Priority)
    if (!isOnline) {
      toast.loading("ネットワーク接続がありません", {
        id: toastIdRef.current,
        description: "再接続を待機しています...",
        duration: Infinity,
      });
      return;
    }

    // 2. Connection Status Handling
    switch (type) {
      case "error": {
        // エラー（リトライ上限到達など）
        toast.error("接続できませんでした", {
          id: toastIdRef.current,
          description: "ページを再読み込みしてください",
          icon: <WifiOff className="h-4 w-4" />,
          duration: Infinity,
        });

        break;
      }
      case "reconnecting": {
        // DebounceされたReconnectingのみ表示
        if (debouncedReconnecting) {
          toast.loading(
            `再接続を試みています... (${String(attempt)}/${String(maxAttempts)})`,
            {
              id: toastIdRef.current,
              description: "",
              duration: Infinity,
            },
          );
        }

        break;
      }
      case "connected": {
        toast.success("接続しました", {
          id: toastIdRef.current,
          description: "",
          icon: <Wifi className="h-4 w-4" />,
          duration: 2000,
        });

        break;
      }
      case "disconnected": {
        // Disconnected logic: Do nothing to prevent flickering.
        // Reconnecting will handle the toast after debounce.

        break;
      }
      // No default
    }
  }, [type, attempt, maxAttempts, isOnline, debouncedReconnecting]);
};

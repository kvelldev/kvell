import { useEffect, useRef } from "react";
import { toast } from "sonner";
import { Wifi, WifiOff } from "lucide-react"; // Loader2は不要になります
import type { ConnectionStatus } from "./useTimelineStream";

export const useConnectionToast = (status: ConnectionStatus) => {
  const toastIdRef = useRef<string | number>("connection-status");

  const { type } = status;
  const attempt = status.type === "reconnecting" ? status.attempt : 0;
  const maxAttempts = status.type === "reconnecting" ? status.maxAttempts : 0;

  useEffect(() => {
    if (type === "reconnecting") {
      toast.loading(`再接続を試みています... (${attempt}/${maxAttempts})`, {
        id: toastIdRef.current,
        description: "",
        duration: Infinity,
      });
    } else if (type === "connected") {
      toast.success("接続しました", {
        id: toastIdRef.current,
        description: "",
        icon: <Wifi className="h-4 w-4" />,
        duration: 2000,
      });
    } else if (type === "error") {
      toast.error("接続できませんでした", {
        id: toastIdRef.current,
        description: "ページを再読み込みしてください",
        icon: <WifiOff className="h-4 w-4" />,
        duration: Infinity,
      });
    } else if (type === "disconnected") {
      toast.loading("接続しています...", {
        id: toastIdRef.current,
        description: "",
        duration: Infinity,
      });
    }
  }, [type, attempt, maxAttempts]);
};

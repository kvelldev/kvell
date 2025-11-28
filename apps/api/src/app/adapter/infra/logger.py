import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

import sentry_sdk
from usecase.ports.logger import ILogger


class JsonLogger(ILogger):
    def __init__(self, service_name: str = "kvell-api"):
        self.service_name = service_name
        # 標準ライブラリのLoggerを設定（JSON化するためフォーマットは無効化）
        self._logger = logging.getLogger(service_name)
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        self._logger.addHandler(handler)

    def _log(
        self,
        level: str,
        event_id: str,
        message: str,
        context: dict | None = None,
        error: Exception | None = None,
    ):
        # 構造化ログの構築
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "service": self.service_name,
            "event_id": event_id,
            "message": message,
            "context": context or {},
        }

        if error:
            log_entry["error"] = {"type": type(error).__name__, "message": str(error)}

        # CloudWatch Logsがパースしやすいよう、1行のJSON文字列として出力
        print(json.dumps(log_entry, ensure_ascii=False))

    def info(
        self, event_id: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        self._log("INFO", event_id, message, context)

    def warn(
        self, event_id: str, message: str, context: dict[str, Any] | None = None
    ) -> None:
        self._log("WARN", event_id, message, context)

    def error(
        self,
        event_id: str,
        message: str,
        error: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        # 1. CloudWatchへ出力
        self._log("ERROR", event_id, message, context, error)

        # 2. Sentryへ送信 (Sentryが初期化されている場合)
        #    明示的にcapture_exceptionすることで、コンテキスト情報も付与できる
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("event_id", event_id)
            if context:
                scope.set_context("app_context", context)
            sentry_sdk.capture_exception(
                error
            ) if error else sentry_sdk.capture_message(message)

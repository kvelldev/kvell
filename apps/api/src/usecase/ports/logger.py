from abc import ABC, abstractmethod
from typing import Any, Optional


class ILogger(ABC):
    """
    アプリケーションログの出力ポート。
    技術的な詳細（Sentry, CloudWatch, Console等）はAdapter層で実装する。
    """

    @abstractmethod
    def info(
        self, event_id: str, message: str, context: Optional[dict[str, Any]] = None
    ) -> None:
        """正常系イベント"""
        pass

    @abstractmethod
    def warn(
        self, event_id: str, message: str, context: Optional[dict[str, Any]] = None
    ) -> None:
        """警告（エラーではないが注意が必要な状態）"""
        pass

    @abstractmethod
    def error(
        self,
        event_id: str,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        異常系イベント。
        本番環境ではエラー追跡ツールへの通知トリガーとなる。
        """
        pass

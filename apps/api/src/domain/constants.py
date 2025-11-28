from typing import Final

INTERNAL_STATUSES: Final[dict[int, str]] = {
    # Success
    200: "OK",
    201: "Created",
    204: "No Content",
    # Domain Errors (Client side origin / Business Logic)
    1001: "この種火は既に燃え尽きています。",  # Gone (Life expired)
    1002: "投稿に不適切な表現が含まれています。",  # NG Words (Validation)
    1003: "投稿文字数が制限を超えています。",  # Length Limit (Validation)
    1004: "薪をくべるペースが早すぎます。",  # Throttling (Rate Limit)
    1005: "指定された種火が存在しないか、消滅しています。",  # Not Found
    # Error caused by Server side (System Error)
    2001: "DBへの接続中に異常が発生しました",
    2002: "{tableName}テーブルへのクエリ中に異常が発生しました",
    500: "Internal Server Error",
}

InternalStatusCode = int

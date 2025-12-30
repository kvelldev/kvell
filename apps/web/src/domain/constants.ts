export const internalStatuses = {
  // Sucess
  200: "OK",
  201: "Created",
  204: "No Content",
  // Client Errors
  400: "Bad Request",
  401: "Unauthorized",
  403: "Forbidden",
  404: "Not Found",
  409: "Conflict",
  422: "Unprocessable Entity",
  // Business Logic Errors
  1001: "Invalid email format.",
  // Server Errors
  500: "Internal Server Error",
} as const;

/**
 * Type representing valid internal status codes.
 */
export type InternalStatusCodes = keyof typeof internalStatuses;

/**
 * Log Event IDs for structured logging.
 * Use these constants in logger calls for testable, consistent event tracking.
 */
export const LOG_EVENTS = {
  // Health Check
  HEALTH_CHECK: {
    FETCH_START: "HEALTH_FETCH_START",
    FETCH_SUCCESS: "HEALTH_FETCH_SUCCESS",
    FETCH_ERROR: "HEALTH_FETCH_ERROR",
    SAVE_START: "HEALTH_SAVE_START",
    SAVE_SUCCESS: "HEALTH_SAVE_SUCCESS",
    SAVE_ERROR: "HEALTH_SAVE_ERROR",
  },
  // Spark Post
  SPARK: {
    POST_START: "SPARK_POST_START",
    POST_SUCCESS: "SPARK_POST_SUCCESS",
    POST_ERROR: "SPARK_POST_ERROR",
  },
  // Add Fuel (薪をくべる)
  ADD_FUEL: {
    START: "ADD_FUEL_START",
    SUCCESS: "ADD_FUEL_SUCCESS",
    ERROR: "ADD_FUEL_ERROR",
    HAPTIC_NOT_SUPPORTED: "ADD_FUEL_HAPTIC_NOT_SUPPORTED",
  },
} as const;

/**
 * Spark cooling threshold ratio
 * Sparks with less than this percentage of their total lifetime remaining
 * will display as "cooling" (ash)
 *
 * This value is derived from the BDD specification:
 * "システムの '冷却閾値' は 'Decay time' に対して '30%' の割合である"
 */
export const COOLING_THRESHOLD_RATIO = 0.3;

/**
 * Available Fields (Communities)
 *
 * Defines the available timeline fields users can join.
 * IDs must match the backend VALID_FIELDS constant.
 */
export const FIELDS = [
  {
    id: "nhk",
    label: "NHK",
    description: "有馬記念、紅白歌合戦、ゆく年くる年、大河ドラマ",
    themeColor: "from-gray-500 to-gray-700",
  },
  {
    id: "ntv",
    label: "日テレ",
    description: "箱根駅伝、高校サッカー、金曜ロードショー",
    themeColor: "from-yellow-400 to-orange-500",
  },
  {
    id: "tvasahi",
    label: "テレ朝",
    description: "芸能人格付けチェック、M-1、アメトーーク",
    themeColor: "from-pink-500 to-rose-500",
  },
  {
    id: "tbs",
    label: "TBS",
    description:
      "レコ大、ザ・イロモネア、ニューイヤー駅伝、ドリーム東西ネタ合戦",
    themeColor: "from-blue-400 to-cyan-400",
  },
  {
    id: "fujitv",
    label: "フジテレビ",
    description: "ドッキリGP、新しいカギ、ミリオネア、逃走中",
    themeColor: "from-teal-400 to-emerald-400",
  },
  {
    id: "tvtokyo",
    label: "テレ東",
    description: "路線バス、あちこちオードリー、出川哲朗の充電旅",
    themeColor: "from-red-500 to-red-700",
  },
  {
    id: "sakurazaka46",
    label: "櫻坂46",
    description: "櫻坂46に関する話題ならなんでも。",
    themeColor: "from-pink-400 to-red-400",
  },
] as const;

/**
 * Field ID type derived from the VALID_FIELDS constant.
 */
export type FieldId = (typeof FIELDS)[number]["id"];

/**
 * Haptic Feedback Utility
 *
 * Provides vibration feedback for supported devices.
 * Non-intrusive: fails silently on unsupported devices.
 */

/**
 * Trigger a short, sharp vibration (10-15ms) for tactile feedback
 * when adding fuel to a spark.
 * @returns true if vibration was triggered, false if unsupported
 */
export const triggerHapticFeedback = (): boolean => {
  if (typeof navigator !== "undefined" && "vibrate" in navigator) {
    try {
      // 15ms short vibration for "add fuel" tactile feedback
      navigator.vibrate(15);
      return true;
    } catch {
      // Fail silently if vibrate() throws an error
      return false;
    }
  }
  return false;
};

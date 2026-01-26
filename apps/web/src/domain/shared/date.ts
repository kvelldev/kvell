/**
 * Format a date string into "MM/DD(Day) HH:mm" format
 * Example: 2024-12-25T16:02:00 -> "12/25(木) 16:02"
 *
 * @param dateString ISO date string
 * @returns Formatted date string
 */
export const formatSparkDate = (dateString: string): string => {
  if (!dateString) return "";
  const date = new Date(dateString);

  // Check for invalid date
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const day = date.getDate().toString().padStart(2, "0");

  const weekdays = ["日", "月", "火", "水", "木", "金", "土"];
  const weekday = weekdays[date.getDay()];

  const hours = date.getHours().toString().padStart(2, "0");
  const minutes = date.getMinutes().toString().padStart(2, "0");

  return `${month}/${day}(${weekday}) ${hours}:${minutes}`;
};

/**
 * ReadMarker Atom
 *
 * A visual indicator showing "ここまで読んだ" (read up to here)
 * Used in bonfire detail view to mark the last read position.
 */

interface ReadMarkerProps {
  /**
   * Optional custom label text
   * @default "ここまで読んだ"
   */
  label?: string;
}

export const ReadMarker = ({ label = "ここまで読んだ" }: ReadMarkerProps) => {
  return (
    <div className="flex items-center gap-3 py-4" data-testid="read-marker">
      <div className="bg-ash-500/30 h-px flex-1" />
      <span className="text-ash-500 text-xs">{label}</span>
      <div className="bg-ash-500/30 h-px flex-1" />
    </div>
  );
};

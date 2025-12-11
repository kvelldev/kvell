/**
 * Action Form Molecule
 *
 * Input form with action buttons for health check (Dumb Component).
 */

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface ActionFormProps {
  inputValue: string;
  onInputChange: (value: string) => void;
  onSave: () => void;
  onFetch: () => void;
  isLoading: boolean;
}

export const ActionForm = ({
  inputValue,
  onInputChange,
  onSave,
  onFetch,
  isLoading,
}: ActionFormProps) => {
  return (
    <div className="space-y-4">
      <div>
        <label className="mb-2 block text-sm font-light text-smoke-100">
          Test Message
        </label>
        <Input
          value={inputValue}
          onChange={(e) => {
            onInputChange(e.target.value);
          }}
          placeholder="Enter a test message..."
          disabled={isLoading}
          data-testid="health-echo-input"
        />
      </div>

      <div className="flex gap-2">
        <Button
          onClick={onSave}
          disabled={isLoading || !inputValue.trim()}
          data-testid="health-save-button"
        >
          Save to DB
        </Button>
        <Button
          onClick={onFetch}
          disabled={isLoading}
          variant="secondary"
          data-testid="health-fetch-button"
        >
          Fetch Latest
        </Button>
      </div>
    </div>
  );
};

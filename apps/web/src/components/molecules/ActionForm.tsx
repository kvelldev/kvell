/**
 * Action Form Molecule
 *
 * Input form with action buttons for health check (Dumb Component).
 */

import { Input } from "@/components/atoms/Input";
import { Button } from "@/components/atoms/Button";

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
        <label className="block text-sm font-light text-smoke-100 mb-2">
          Test Message
        </label>
        <Input
          value={inputValue}
          onChange={onInputChange}
          placeholder="Enter a test message..."
          disabled={isLoading}
          testId="health-echo-input"
        />
      </div>

      <div className="flex gap-2">
        <Button
          onClick={onSave}
          disabled={isLoading || !inputValue.trim()}
          testId="health-save-button"
        >
          Save to DB
        </Button>
        <Button
          onClick={onFetch}
          disabled={isLoading}
          variant="secondary"
          testId="health-fetch-button"
        >
          Fetch Latest
        </Button>
      </div>
    </div>
  );
};

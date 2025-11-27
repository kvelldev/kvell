/**
 * Health Check Page
 * 
 * Page component for E2E health check (Smart Component).
 */

import { useState } from 'react';
import { useHealthCheck } from '@/usecase/useHealthCheck';
import { Button } from '@/components/atoms/Button';
import { Input } from '@/components/atoms/Input';

export const HealthCheckPage = () => {
  const [inputText, setInputText] = useState('');
  const { message, isLoading, error, saveMessage, fetchLatest } = useHealthCheck();

  const handleSave = async () => {
    if (!inputText.trim()) return;
    await saveMessage(inputText);
    setInputText('');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 text-center">
          System Health Check
        </h1>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Message
            </label>
            <Input
              value={inputText}
              onChange={setInputText}
              placeholder="Enter a test message..."
              disabled={isLoading}
            />
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleSave}
              disabled={isLoading || !inputText.trim()}
            >
              Save to DB
            </Button>
            <Button
              onClick={fetchLatest}
              disabled={isLoading}
              variant="secondary"
            >
              Fetch Latest
            </Button>
          </div>
        </div>

        {isLoading && (
          <div className="text-center text-gray-600">
            Loading...
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800 text-sm font-medium">Error</p>
            <p className="text-red-600 text-sm">{error.message}</p>
          </div>
        )}

        {message && !error && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <p className="text-green-800 text-sm font-medium">Success</p>
            <p className="text-green-700 text-sm mt-1">
              <strong>Message:</strong> {message.message}
            </p>
            <p className="text-green-600 text-xs mt-1">
              ID: {message.id}
            </p>
            <p className="text-green-600 text-xs">
              Created: {new Date(message.createdAt).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

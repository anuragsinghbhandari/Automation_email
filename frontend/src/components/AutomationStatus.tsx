import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import axios from 'axios';

interface AutomationStatusProps {
  onStart: () => Promise<void>;
}

const AutomationStatus: React.FC<AutomationStatusProps> = ({ onStart }) => {
  const [status, setStatus] = useState<'idle' | 'processing' | 'started'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [emailReceived, setEmailReceived] = useState<string | null>(null);
  const [emailSent, setEmailSent] = useState<string | null>(null);

  const fetchEmailStatus = async () => {
    try {
      const response = await axios.get('http://localhost:5000/email-status');
      setEmailReceived(response.data.received);
      setEmailSent(response.data.sent);
    } catch (err) {
      console.error('Error fetching email status:', err);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchEmailStatus, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleStartAutomation = async () => {
    try {
      setStatus('processing');
      setError(null);
      await onStart();
      setStatus('started');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start automation');
      setStatus('idle');
    }
  };

  const isRunning = status === 'started';
  const isProcessing = status === 'processing';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity
            className={`h-6 w-6 ${isRunning ? 'text-green-500' : 'text-gray-400'}`}
          />
          <div>
            <h3 className="text-lg font-medium text-gray-900">Automation Status</h3>
            <p className="text-sm text-gray-500">
              {isRunning
                ? 'Currently monitoring emails'
                : isProcessing
                ? 'Processing...'
                : 'Automation is stopped'}
            </p>
          </div>
        </div>
        <button
          onClick={handleStartAutomation}
          disabled={isProcessing}
          className={`px-4 py-2 rounded-lg font-medium ${
            isRunning
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : isProcessing
              ? 'bg-gray-100 text-gray-700 cursor-not-allowed'
              : 'bg-green-100 text-green-700 hover:bg-green-200'
          }`}
        >
          {isRunning ? 'Started' : isProcessing ? 'Processing...' : 'Start Automation'}
        </button>
      </div>
      {error && <p className="text-red-500 mt-4">{error}</p>}
      {emailReceived && <p className="text-gray-600 mt-2">{emailReceived}</p>}
      {emailSent && <p className="text-gray-600 mt-2">{emailSent}</p>}
    </div>
  );
};

export default AutomationStatus;

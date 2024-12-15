import React from 'react';
import { Activity } from 'lucide-react';

interface AutomationStatusProps {
  isRunning: boolean;
  onStart: () => void;
  onStop: () => void;
}

const AutomationStatus: React.FC<AutomationStatusProps> = ({
  isRunning,
  onStart,
  onStop,
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className={`h-6 w-6 ${isRunning ? 'text-green-500' : 'text-gray-400'}`} />
          <div>
            <h3 className="text-lg font-medium text-gray-900">Automation Status</h3>
            <p className="text-sm text-gray-500">
              {isRunning ? 'Currently monitoring emails' : 'Automation is stopped'}
            </p>
          </div>
        </div>
        <button
          onClick={isRunning ? onStop : onStart}
          className={`px-4 py-2 rounded-lg font-medium ${
            isRunning
              ? 'bg-red-100 text-red-700 hover:bg-red-200'
              : 'bg-green-100 text-green-700 hover:bg-green-200'
          }`}
        >
          {isRunning ? 'Stop' : 'Start'} Automation
        </button>
      </div>
    </div>
  );
};

export default AutomationStatus;
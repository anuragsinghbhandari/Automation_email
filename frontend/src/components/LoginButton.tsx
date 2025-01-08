import React from 'react';
import { Mail } from 'lucide-react';

interface LoginButtonProps {
  onClick: () => void;
  isLoading: boolean;
}

const LoginButton: React.FC<LoginButtonProps> = ({ onClick, isLoading }) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
    >
      <Mail className="h-5 w-5" />
      <span>{isLoading ? 'Connecting...' : 'Connect with Gmail'}</span>
    </button>
  );
};

export default LoginButton;
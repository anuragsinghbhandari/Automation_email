import React from 'react';
import { Mail } from 'lucide-react';

interface LoginButtonProps {
  isLoading: boolean;
}

const LoginButton: React.FC<LoginButtonProps> = ({ isLoading }) => {
  const handleLogin = () => {
    // Redirect to the backend login route
    window.location.href = "http://localhost:5000/login";
  };

  return (
    <button
      onClick={handleLogin}
      disabled={isLoading}
      className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
    >
      <Mail className="h-5 w-5" />
      <span>{isLoading ? 'Connecting...' : 'Connect with Gmail'}</span>
    </button>
  );
};

export default LoginButton;

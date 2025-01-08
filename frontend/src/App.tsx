import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import LoginButton from './components/LoginButton';
import FileUpload from './components/FileUpload';
import AutomationStatus from './components/AutomationStatus';
import type { AuthState, UploadState } from './types';

const API_URL = 'https://automation-email.onrender.com';

// Configure axios defaults
axios.defaults.withCredentials = true;

function App() {
  const [auth, setAuth] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,  // Start with loading true
  });

  const [upload, setUpload] = useState<UploadState>({
    files: [],
    isUploading: false,
  });

  const [isAutomationRunning, setIsAutomationRunning] = useState(false);

  const checkAuth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/status`);
      setAuth({
        isAuthenticated: response.data.isAuthenticated,
        isLoading: false,
      });
    } catch (error) {
      console.error('Auth check failed:', error);
      setAuth({
        isAuthenticated: false,
        isLoading: false,
      });
    }
  }, []);

  useEffect(() => {
    // Check auth status immediately when component mounts
    checkAuth();

    // Set up interval to periodically check auth status
    const interval = setInterval(checkAuth, 5000);

    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, [checkAuth]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const authStatus = params.get('auth');
    const errorMessage = params.get('message');

    if (authStatus === 'success') {
      toast.success('Successfully logged in!');
      checkAuth();
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authStatus === 'error') {
      toast.error(`Login failed: ${errorMessage || 'Unknown error'}`);
      setAuth({ isAuthenticated: false, isLoading: false });
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [checkAuth]);

  const handleLogin = useCallback(async () => {
    try {
      setAuth(prev => ({ ...prev, isLoading: true }));
      const response = await axios.get(`${API_URL}/login`);
      window.location.href = response.data.url;
    } catch (error) {
      toast.error('Failed to initialize login');
      setAuth(prev => ({ ...prev, isLoading: false }));
    }
  }, []);

  // Rest of your component remains the same...

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <Header 
        isAuthenticated={auth.isAuthenticated} 
        onLogout={handleLogout}
      />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          {auth.isLoading ? (
            <div className="flex justify-center items-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
            </div>
          ) : !auth.isAuthenticated ? (
            <div className="flex flex-col items-center justify-center space-y-4">
              <h2 className="text-2xl font-semibold text-gray-900">
                Connect Your Gmail Account
              </h2>
              <p className="text-gray-600 text-center max-w-md">
                Allow access to your Gmail account to enable automated email responses
                powered by AI.
              </p>
              <LoginButton onClick={handleLogin} isLoading={auth.isLoading} />
            </div>
          ) : (
            <>
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Upload Knowledge Base
                  </h2>
                  <FileUpload
                    files={upload.files}
                    onFileSelect={handleFileSelect}
                    onFileRemove={handleFileRemove}
                    isUploading={upload.isUploading}
                  />
                </div>

                <AutomationStatus
                  isRunning={isAutomationRunning}
                  onStart={handleStartAutomation}
                  onStop={handleStopAutomation}
                />
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
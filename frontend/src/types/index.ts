export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface UploadState {
  files: File[];
  isUploading: boolean;
}
import React, { useCallback } from 'react';
import { Upload, X } from 'lucide-react';

interface FileUploadProps {
  files: File[];
  onFileSelect: (files: FileList) => void;
  onFileRemove: (index: number) => void;
  isUploading: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  files,
  onFileSelect,
  onFileRemove,
  isUploading,
}) => {
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (e.dataTransfer.files) {
        onFileSelect(e.dataTransfer.files);
      }
    },
    [onFileSelect]
  );

  return (
    <div className="w-full max-w-md">
      <div
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors"
      >
        <input
          type="file"
          id="file-upload"
          multiple
          accept=".pdf"
          className="hidden"
          onChange={(e) => e.target.files && onFileSelect(e.target.files)}
          disabled={isUploading}
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center space-y-2"
        >
          <Upload className="h-12 w-12 text-gray-400" />
          <span className="text-gray-600">
            Drop PDF files here or click to upload
          </span>
        </label>
      </div>

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-gray-50 p-2 rounded"
            >
              <span className="truncate flex-1">{file.name}</span>
              <button
                onClick={() => onFileRemove(index)}
                className="text-red-500 hover:text-red-700"
                disabled={isUploading}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
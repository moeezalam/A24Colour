import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, X } from 'lucide-react';

interface ImageUploadProps {
  onImageUpload: (file: File) => void;
  uploadedImage: File | null;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onImageUpload, uploadedImage }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onImageUpload(acceptedFiles[0]);
    }
  }, [onImageUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const clearImage = () => {
    onImageUpload(null as any);
  };

  if (uploadedImage) {
    return (
      <div className="relative">
        <div className="bg-gray-900 rounded-lg p-4 border-2 border-gray-600">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-green-400">
              <Image size={20} />
              <span className="font-medium">Image Ready</span>
            </div>
            <button
              onClick={clearImage}
              className="text-gray-400 hover:text-red-400 transition-colors"
            >
              <X size={20} />
            </button>
          </div>
          
          <div className="bg-gray-800 rounded p-3">
            <img
              src={URL.createObjectURL(uploadedImage)}
              alt="Uploaded"
              className="w-full h-48 object-cover rounded"
            />
            <div className="mt-2 text-sm text-gray-400">
              <p><strong>Name:</strong> {uploadedImage.name}</p>
              <p><strong>Size:</strong> {(uploadedImage.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
        transition-all duration-200
        ${isDragActive 
          ? 'border-blue-400 bg-blue-400/10' 
          : 'border-gray-600 bg-gray-900/50 hover:border-gray-500'
        }
      `}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto mb-4 text-gray-400" size={48} />
      
      {isDragActive ? (
        <p className="text-blue-400 font-medium">Drop your image here...</p>
      ) : (
        <div className="space-y-2">
          <p className="text-gray-300 font-medium">
            Drag & drop your image here
          </p>
          <p className="text-gray-500 text-sm">
            or click to browse files
          </p>
          <p className="text-gray-600 text-xs">
            Supports: JPG, PNG, BMP, TIFF (Max: 10MB)
          </p>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
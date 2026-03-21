import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import StyleSelector from './components/StyleSelector';
import ProcessingStatus from './components/ProcessingStatus';
import ResultDisplay from './components/ResultDisplay';
import { useImageProcessing } from './hooks/useImageProcessing';
import { ProcessingRequest, StylePreset } from './types';

const App: React.FC = () => {
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<string>('moonlight');
  const [customSettings, setCustomSettings] = useState<Partial<StylePreset>>({});
  
  const {
    processImage,
    isProcessing,
    progress,
    result,
    error,
    reset
  } = useImageProcessing();

  const handleImageUpload = (file: File) => {
    setUploadedImage(file);
    reset(); // Clear previous results
  };

  const handleStyleChange = (style: string) => {
    setSelectedStyle(style);
  };

  const handleProcess = async () => {
    if (!uploadedImage) return;

    const request: ProcessingRequest = {
      style: selectedStyle,
      customSettings: Object.keys(customSettings).length > 0 ? customSettings : undefined
    };

    await processImage(uploadedImage, request);
  };

  const handleReset = () => {
    setUploadedImage(null);
    setSelectedStyle('moonlight');
    setCustomSettings({});
    reset();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-white mb-2">
            A24 Style Transfer
          </h1>
          <p className="text-gray-300">
            Transform your photos with cinematic A24 aesthetics
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Controls */}
          <div className="space-y-6">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
              <h2 className="text-2xl font-semibold text-white mb-4">
                Upload & Configure
              </h2>
              
              <ImageUpload 
                onImageUpload={handleImageUpload}
                uploadedImage={uploadedImage}
              />
              
              {uploadedImage && (
                <>
                  <StyleSelector
                    selectedStyle={selectedStyle}
                    onStyleChange={handleStyleChange}
                    customSettings={customSettings}
                    onCustomSettingsChange={setCustomSettings}
                  />
                  
                  <div className="mt-6 flex gap-4">
                    <button
                      onClick={handleProcess}
                      disabled={isProcessing}
                      className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 
                                text-white py-3 px-6 rounded-lg font-semibold
                                hover:from-blue-500 hover:to-purple-500 
                                disabled:opacity-50 disabled:cursor-not-allowed
                                transition-all duration-200"
                    >
                      {isProcessing ? 'Processing...' : 'Apply A24 Style'}
                    </button>
                    
                    <button
                      onClick={handleReset}
                      disabled={isProcessing}
                      className="px-6 py-3 border border-gray-600 text-gray-300 
                                rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      Reset
                    </button>
                  </div>
                </>
              )}
            </div>

            {isProcessing && (
              <ProcessingStatus progress={progress} />
            )}

            {error && (
              <div className="bg-red-900/20 border border-red-700 rounded-xl p-4">
                <h3 className="text-red-400 font-semibold mb-2">Processing Error</h3>
                <p className="text-red-300">{error}</p>
              </div>
            )}
          </div>

          {/* Right Panel - Results */}
          <div className="space-y-6">
            <ResultDisplay
              originalImage={uploadedImage}
              processedImage={result}
              selectedStyle={selectedStyle}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
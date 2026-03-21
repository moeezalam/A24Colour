import React, { useState } from 'react';
import { Download, Eye, EyeOff, Maximize2, Film } from 'lucide-react';

interface ResultDisplayProps {
  originalImage: File | null;
  processedImage: string | null;
  selectedStyle: string;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({
  originalImage,
  processedImage,
  selectedStyle
}) => {
  const [showComparison, setShowComparison] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const downloadImage = () => {
    if (!processedImage) return;

    const link = document.createElement('a');
    link.href = processedImage;
    link.download = `a24-${selectedStyle}-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!originalImage && !processedImage) {
    return (
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-8 border border-gray-700">
        <div className="text-center text-gray-400">
          <Film className="mx-auto mb-4" size={48} />
          <p className="text-lg">Your A24-styled image will appear here</p>
          <p className="text-sm mt-2">Upload an image and select a style to get started</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">
            {processedImage ? 'Result' : 'Preview'}
          </h3>
          
          <div className="flex items-center gap-2">
            {originalImage && processedImage && (
              <button
                onClick={() => setShowComparison(!showComparison)}
                className="p-2 text-gray-400 hover:text-white transition-colors"
                title={showComparison ? 'Hide comparison' : 'Show comparison'}
              >
                {showComparison ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            )}
            
            {processedImage && (
              <>
                <button
                  onClick={() => setIsFullscreen(true)}
                  className="p-2 text-gray-400 hover:text-white transition-colors"
                  title="View fullscreen"
                >
                  <Maximize2 size={20} />
                </button>
                
                <button
                  onClick={downloadImage}
                  className="flex items-center gap-2 bg-green-600 hover:bg-green-500 
                           text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <Download size={16} />
                  Download
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Image Display */}
      <div className="p-4">
        {showComparison && originalImage && processedImage ? (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-400 mb-2">Original</p>
              <img
                src={URL.createObjectURL(originalImage)}
                alt="Original"
                className="w-full h-auto rounded-lg"
              />
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-2">A24 Style ({selectedStyle})</p>
              <img
                src={processedImage}
                alt="Processed"
                className="w-full h-auto rounded-lg"
              />
            </div>
          </div>
        ) : processedImage ? (
          <div>
            <p className="text-sm text-gray-400 mb-2">A24 Style ({selectedStyle})</p>
            <img
              src={processedImage}
              alt="Processed"
              className="w-full h-auto rounded-lg"
            />
          </div>
        ) : originalImage ? (
          <div>
            <p className="text-sm text-gray-400 mb-2">Original</p>
            <img
              src={URL.createObjectURL(originalImage)}
              alt="Original"
              className="w-full h-auto rounded-lg"
            />
          </div>
        ) : null}
      </div>

      {/* Fullscreen Modal */}
      {isFullscreen && processedImage && (
        <div 
          className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
          onClick={() => setIsFullscreen(false)}
        >
          <div className="max-w-screen-lg max-h-screen">
            <img
              src={processedImage}
              alt="Processed Fullscreen"
              className="max-w-full max-h-full object-contain"
            />
          </div>
          <button
            onClick={() => setIsFullscreen(false)}
            className="absolute top-4 right-4 text-white hover:text-gray-300 text-2xl"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultDisplay;
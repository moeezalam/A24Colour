import React from 'react';
import { Loader2, Film, Brain } from 'lucide-react';

interface ProcessingStatusProps {
  progress: number;
  message?: string;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ progress, message }) => {
  const stages = [
    'Analyzing image...',
    'Applying color grading...',
    'Simulating lighting...',
    'Adding film texture...',
    'Finalizing composition...'
  ];

  const currentStage = Math.min(Math.floor(progress / 20), stages.length - 1);

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
      <div className="flex items-center gap-3 mb-4">
        <div className="flex items-center gap-2">
          <Brain className="text-purple-400" size={20} />
          <Loader2 className="text-blue-400 animate-spin" size={24} />
        </div>
        <div>
          <h3 className="text-xl font-semibold text-white">
            AI Processing Your Image
          </h3>
          <p className="text-sm text-purple-300">Powered by TensorFlow Hub</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>{message || stages[currentStage]}</span>
            <span>{progress.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Stage Indicators */}
        <div className="grid grid-cols-5 gap-2 mt-6">
          {stages.map((stage, index) => (
            <div
              key={index}
              className={`text-center transition-all duration-300 ${
                index <= currentStage
                  ? 'text-blue-400'
                  : 'text-gray-600'
              }`}
            >
              <div
                className={`w-8 h-8 mx-auto rounded-full border-2 flex items-center justify-center mb-2 ${
                  index < currentStage
                    ? 'border-blue-500 bg-blue-500'
                    : index === currentStage
                    ? 'border-blue-400 bg-blue-400/20'
                    : 'border-gray-600'
                }`}
              >
                {index < currentStage ? (
                  <Film size={16} className="text-white" />
                ) : index === currentStage ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <span className="text-xs">{index + 1}</span>
                )}
              </div>
              <p className="text-xs leading-tight">{stage.split(' ')[0]}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProcessingStatus;
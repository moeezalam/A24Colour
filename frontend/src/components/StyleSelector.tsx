import React from 'react';
import { ChevronDown, Sliders } from 'lucide-react';
import { StylePreset } from '../types';

interface StyleSelectorProps {
  selectedStyle: string;
  onStyleChange: (style: string) => void;
  customSettings: Partial<StylePreset>;
  onCustomSettingsChange: (settings: Partial<StylePreset>) => void;
}

const StyleSelector: React.FC<StyleSelectorProps> = ({
  selectedStyle,
  onStyleChange,
  customSettings,
  onCustomSettingsChange
}) => {
  const [showAdvanced, setShowAdvanced] = React.useState(false);

  const styles = [
    {
      id: 'moonlight',
      name: 'Moonlight',
      description: 'Dreamy cyan-magenta coastal atmosphere',
      color: 'from-cyan-500 to-pink-500'
    },
    {
      id: 'hereditary',
      name: 'Hereditary', 
      description: 'Warm interiors with unsettling green shadows',
      color: 'from-orange-500 to-green-600'
    },
    {
      id: 'green_knight',
      name: 'The Green Knight',
      description: 'Medieval earthiness with candlelit warmth',
      color: 'from-green-700 to-yellow-600'
    },
    {
      id: 'lighthouse',
      name: 'The Lighthouse',
      description: 'Black and white claustrophobic atmosphere',
      color: 'from-gray-600 to-gray-800'
    },
    {
      id: 'eighth_grade',
      name: 'Eighth Grade',
      description: 'Natural digital look with subtle warmth',
      color: 'from-blue-400 to-pink-400'
    },
    {
      id: 'midsommar',
      name: 'Midsommar',
      description: 'Bright daylight horror with saturated pastels',
      color: 'from-yellow-400 to-green-400'
    }
  ];

  const handleSliderChange = (key: string, value: number) => {
    onCustomSettingsChange({
      ...customSettings,
      [key]: value
    });
  };

  return (
    <div className="space-y-6 mt-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-3">
          Choose A24 Style
        </h3>
        
        <div className="grid grid-cols-1 gap-3">
          {styles.map((style) => (
            <button
              key={style.id}
              onClick={() => onStyleChange(style.id)}
              className={`
                relative p-4 rounded-lg border-2 text-left transition-all
                ${selectedStyle === style.id
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-600 bg-gray-800/50 hover:border-gray-500'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full bg-gradient-to-r ${style.color}`} />
                <div>
                  <div className="font-semibold text-white">{style.name}</div>
                  <div className="text-sm text-gray-400">{style.description}</div>
                </div>
              </div>
              
              {selectedStyle === style.id && (
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Settings */}
      <div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
        >
          <Sliders size={16} />
          <span>Advanced Settings</span>
          <ChevronDown 
            size={16} 
            className={`transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
          />
        </button>

        {showAdvanced && (
          <div className="mt-4 space-y-4 p-4 bg-gray-800/30 rounded-lg border border-gray-700">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Desaturation: {((customSettings.desaturation || 0.3) * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customSettings.desaturation || 0.3}
                onChange={(e) => handleSliderChange('desaturation', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Grain Intensity: {((customSettings.grain_intensity || 0.3) * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={customSettings.grain_intensity || 0.3}
                onChange={(e) => handleSliderChange('grain_intensity', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Shadow Lift: {((customSettings.shadow_lift || 0.1) * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="0.5"
                step="0.025"
                value={customSettings.shadow_lift || 0.1}
                onChange={(e) => handleSliderChange('shadow_lift', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Aspect Ratio
              </label>
              <select
                value={customSettings.aspect_ratio || 'cinematic'}
                onChange={(e) => onCustomSettingsChange({
                  ...customSettings,
                  aspect_ratio: e.target.value
                })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
              >
                <option value="academy">4:3 (Academy)</option>
                <option value="standard">16:9 (Standard)</option>
                <option value="cinematic">2.39:1 (Cinematic)</option>
                <option value="square">1:1 (Square)</option>
              </select>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StyleSelector;
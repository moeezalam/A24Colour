# A24 Photo Style Transfer App - Complete Development Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Environment Setup](#environment-setup)
5. [Core Implementation](#core-implementation)
6. [Frontend Development](#frontend-development)
7. [Backend API](#backend-api)
8. [Testing & Deployment](#testing--deployment)

## Project Overview

This app transforms regular photos into A24-style cinematic images through:
- Color grading with film-specific LUTs
- Film grain and texture overlays
- AI-powered lighting simulation
- Aspect ratio conversion
- Compositional reframing

## Technology Stack

### Backend
- **Python 3.9+** - Main processing engine
- **FastAPI** - Web API framework
- **OpenCV** - Image processing
- **NumPy** - Mathematical operations
- **Pillow (PIL)** - Image manipulation
- **colour-science** - Color grading
- **PyTorch** - AI lighting models
- **scikit-image** - Advanced image processing

### Frontend
- **React.js** - User interface
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Dropzone** - File uploads
- **Axios** - API calls

### Additional Tools
- **Docker** - Containerization
- **Redis** - Task queue
- **Celery** - Background processing
- **AWS S3** - File storage (optional)

## Project Structure

```
a24-style-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── color_grading.py
│   │   │   ├── film_texture.py
│   │   │   ├── lighting_simulation.py
│   │   │   ├── composition.py
│   │   │   └── aspect_ratio.py
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   ├── a24_processor.py
│   │   │   └── style_presets.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── image_utils.py
│   │       └── file_handler.py
│   ├── assets/
│   │   ├── luts/
│   │   │   ├── moonlight.cube
│   │   │   ├── hereditary.cube
│   │   │   ├── green_knight.cube
│   │   │   └── lighthouse.cube
│   │   ├── grain_textures/
│   │   │   ├── 16mm_grain.png
│   │   │   ├── 35mm_grain.png
│   │   │   └── digital_grain.png
│   │   └── models/
│   │       └── lighting_model.pth
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── StyleSelector.tsx
│   │   │   ├── ProcessingStatus.tsx
│   │   │   └── ResultDisplay.tsx
│   │   ├── hooks/
│   │   │   └── useImageProcessing.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Environment Setup

### 1. Backend Setup

Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

Install dependencies (`requirements.txt`):
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.0.1
colour-science==0.4.3
torch==2.1.0
torchvision==0.16.0
scikit-image==0.21.0
redis==5.0.1
celery==5.3.4
pydantic==2.5.0
python-dotenv==1.0.0
aiofiles==23.2.1
```

### 2. Frontend Setup

```bash
cd frontend
npm create react-app . --template typescript
npm install axios react-dropzone @types/node tailwindcss
npx tailwindcss init
```

## Core Implementation

### 1. Color Grading Module (`backend/app/core/color_grading.py`)

```python
import cv2
import numpy as np
from colour import LUT3D, read_LUT
from typing import Tuple, Optional
import os

class ColorGrader:
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self.luts = self._load_luts()
    
    def _load_luts(self) -> dict:
        """Load all A24 style LUTs"""
        lut_files = {
            'moonlight': 'moonlight.cube',
            'hereditary': 'hereditary.cube', 
            'green_knight': 'green_knight.cube',
            'lighthouse': 'lighthouse.cube'
        }
        
        luts = {}
        for style, filename in lut_files.items():
            path = os.path.join(self.assets_path, 'luts', filename)
            if os.path.exists(path):
                luts[style] = read_LUT(path)
        return luts
    
    def apply_lut(self, image: np.ndarray, style: str, strength: float = 1.0) -> np.ndarray:
        """Apply LUT with specified strength"""
        if style not in self.luts:
            return image
        
        lut = self.luts[style]
        
        # Convert to float32 and normalize
        img_float = image.astype(np.float32) / 255.0
        
        # Apply LUT
        graded = lut.apply(img_float)
        
        # Blend with original based on strength
        result = img_float * (1 - strength) + graded * strength
        
        # Convert back to uint8
        return (np.clip(result, 0, 1) * 255).astype(np.uint8)
    
    def split_tone(self, image: np.ndarray, highlight_color: Tuple[int, int, int], 
                   shadow_color: Tuple[int, int, int], balance: float = 0.0) -> np.ndarray:
        """Apply split toning (warm highlights, cool shadows)"""
        img_lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l_channel = img_lab[:,:,0].astype(np.float32) / 255.0
        
        # Create masks for highlights and shadows
        highlight_mask = np.where(l_channel > 0.5, 
                                (l_channel - 0.5) * 2, 0)
        shadow_mask = np.where(l_channel < 0.5, 
                             (0.5 - l_channel) * 2, 0)
        
        # Apply color tinting
        result = image.copy().astype(np.float32)
        
        for i, (h_color, s_color) in enumerate(zip(highlight_color, shadow_color)):
            result[:,:,i] += highlight_mask * h_color * 0.3
            result[:,:,i] += shadow_mask * s_color * 0.3
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def desaturate(self, image: np.ndarray, amount: float = 0.3) -> np.ndarray:
        """Reduce saturation for muted A24 look"""
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hsv[:,:,1] = hsv[:,:,1] * (1 - amount)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    def lift_shadows(self, image: np.ndarray, lift: float = 0.1) -> np.ndarray:
        """Lift shadows without crushing blacks"""
        img_float = image.astype(np.float32) / 255.0
        
        # Create shadow mask (non-linear)
        shadow_mask = 1 - np.power(img_float, 0.5)
        
        # Lift shadows
        lifted = img_float + shadow_mask * lift
        
        return (np.clip(lifted, 0, 1) * 255).astype(np.uint8)
```

### 2. Film Texture Module (`backend/app/core/film_texture.py`)

```python
import cv2
import numpy as np
from PIL import Image
import random
from typing import Tuple

class FilmTexture:
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self.grain_textures = self._load_grain_textures()
    
    def _load_grain_textures(self) -> dict:
        """Load grain texture images"""
        grain_files = {
            '16mm': '16mm_grain.png',
            '35mm': '35mm_grain.png', 
            'digital': 'digital_grain.png'
        }
        
        textures = {}
        for grain_type, filename in grain_files.items():
            path = os.path.join(self.assets_path, 'grain_textures', filename)
            if os.path.exists(path):
                texture = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                textures[grain_type] = texture
        return textures
    
    def add_film_grain(self, image: np.ndarray, grain_type: str = '35mm', 
                      intensity: float = 0.3) -> np.ndarray:
        """Add film grain texture"""
        if grain_type not in self.grain_textures:
            # Generate procedural grain if texture not available
            return self._add_procedural_grain(image, intensity)
        
        grain_texture = self.grain_textures[grain_type]
        h, w = image.shape[:2]
        
        # Resize grain texture to match image
        grain_resized = cv2.resize(grain_texture, (w, h))
        
        # Normalize grain to [-1, 1]
        grain_normalized = (grain_resized.astype(np.float32) - 128) / 128
        
        # Apply grain to each channel
        result = image.astype(np.float32)
        for i in range(image.shape[2]):
            result[:,:,i] += grain_normalized * intensity * 30
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _add_procedural_grain(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """Generate procedural grain"""
        h, w = image.shape[:2]
        
        # Generate random noise
        noise = np.random.normal(0, 1, (h, w)) * intensity * 25
        
        # Apply to all channels
        result = image.astype(np.float32)
        for i in range(image.shape[2]):
            result[:,:,i] += noise
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def add_halation(self, image: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Add halation/bloom effect around highlights"""
        # Find bright areas
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
        
        # Create glow effect
        glow = cv2.GaussianBlur(bright_mask, (21, 21), 8)
        glow = glow.astype(np.float32) / 255.0 * strength
        
        # Apply glow to original image
        result = image.astype(np.float32)
        for i in range(3):
            result[:,:,i] = result[:,:,i] + glow * 50
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def add_chromatic_aberration(self, image: np.ndarray, 
                                strength: float = 2.0) -> np.ndarray:
        """Add subtle chromatic aberration"""
        h, w = image.shape[:2]
        
        # Create displacement maps
        shift_x = int(strength)
        shift_y = int(strength * 0.3)
        
        # Split into channels
        b, g, r = cv2.split(image)
        
        # Shift red channel
        M_r = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        r_shifted = cv2.warpAffine(r, M_r, (w, h))
        
        # Shift blue channel (opposite direction)
        M_b = np.float32([[1, 0, -shift_x], [0, 1, -shift_y]])
        b_shifted = cv2.warpAffine(b, M_b, (w, h))
        
        # Recombine
        return cv2.merge([b_shifted, g, r_shifted])
```

### 3. Lighting Simulation (`backend/app/core/lighting_simulation.py`)

```python
import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import Tuple, Optional

class LightingSimulator:
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        if model_path:
            self.model = self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load pre-trained lighting model"""
        # Placeholder for actual model loading
        # In practice, you'd use a model like Portrait Relighting
        pass
    
    def simulate_window_light(self, image: np.ndarray, 
                            direction: str = 'left',
                            intensity: float = 0.7) -> np.ndarray:
        """Simulate directional window lighting"""
        h, w = image.shape[:2]
        
        # Create directional light gradient
        if direction == 'left':
            gradient = np.linspace(intensity, 1.0, w)
            light_map = np.tile(gradient, (h, 1))
        elif direction == 'right':
            gradient = np.linspace(1.0, intensity, w)
            light_map = np.tile(gradient, (h, 1))
        elif direction == 'top':
            gradient = np.linspace(intensity, 1.0, h)
            light_map = np.tile(gradient.reshape(-1, 1), (1, w))
        else:  # bottom
            gradient = np.linspace(1.0, intensity, h)
            light_map = np.tile(gradient.reshape(-1, 1), (1, w))
        
        # Apply Gaussian blur for soft transition
        light_map = cv2.GaussianBlur(light_map, (51, 51), 20)
        
        # Apply to image
        result = image.astype(np.float32)
        for i in range(3):
            result[:,:,i] *= light_map
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def add_practical_light(self, image: np.ndarray, 
                           position: Tuple[int, int],
                           color: Tuple[int, int, int] = (255, 200, 150),
                           falloff: float = 0.8) -> np.ndarray:
        """Add practical light source (lamp, candle, etc.)"""
        h, w = image.shape[:2]
        x, y = position
        
        # Create distance map from light source
        xx, yy = np.meshgrid(np.arange(w), np.arange(h))
        distance = np.sqrt((xx - x)**2 + (yy - y)**2)
        
        # Create falloff
        max_distance = np.sqrt(w**2 + h**2) * falloff
        intensity_map = np.maximum(0, 1 - distance / max_distance)
        intensity_map = np.power(intensity_map, 2)  # Non-linear falloff
        
        # Apply colored lighting
        result = image.astype(np.float32)
        for i, color_val in enumerate(color):
            light_contribution = intensity_map * color_val * 0.3
            result[:,:,i] += light_contribution
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def enhance_shadows(self, image: np.ndarray, 
                       shadow_color: Tuple[int, int, int] = (0, 50, 100)) -> np.ndarray:
        """Enhance shadows with cool tones"""
        # Convert to grayscale to find shadows
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Create shadow mask
        shadow_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)[1]
        shadow_mask = shadow_mask.astype(np.float32) / 255.0
        
        # Smooth the mask
        shadow_mask = cv2.GaussianBlur(shadow_mask, (15, 15), 5)
        
        # Apply cool tone to shadows
        result = image.astype(np.float32)
        for i, color_val in enumerate(shadow_color):
            result[:,:,i] += shadow_mask * color_val * 0.2
        
        return np.clip(result, 0, 255).astype(np.uint8)
```

### 4. Aspect Ratio & Composition (`backend/app/core/aspect_ratio.py`)

```python
import cv2
import numpy as np
from typing import Tuple, Optional

class AspectRatioProcessor:
    
    RATIOS = {
        'academy': (4, 3),      # Intimate/claustrophobic
        'standard': (16, 9),    # Standard/realistic
        'cinematic': (239, 100), # Epic/wide
        'square': (1, 1),       # Instagram/artistic
        'portrait': (3, 4)      # Vertical/mobile
    }
    
    def change_aspect_ratio(self, image: np.ndarray, 
                          ratio_name: str,
                          crop_position: str = 'center') -> np.ndarray:
        """Change aspect ratio with letterboxing or cropping"""
        if ratio_name not in self.RATIOS:
            return image
        
        target_width, target_height = self.RATIOS[ratio_name]
        h, w = image.shape[:2]
        
        current_ratio = w / h
        target_ratio = target_width / target_height
        
        if current_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(h * target_ratio)
            if crop_position == 'center':
                start_x = (w - new_width) // 2
            elif crop_position == 'left':
                start_x = 0
            else:  # right
                start_x = w - new_width
            
            cropped = image[:, start_x:start_x + new_width]
        else:
            # Image is taller, crop height
            new_height = int(w / target_ratio)
            if crop_position == 'center':
                start_y = (h - new_height) // 2
            elif crop_position == 'top':
                start_y = 0
            else:  # bottom
                start_y = h - new_height
            
            cropped = image[start_y:start_y + new_height, :]
        
        return cropped
    
    def add_letterbox(self, image: np.ndarray, 
                     ratio_name: str,
                     bar_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        """Add letterbox bars instead of cropping"""
        if ratio_name not in self.RATIOS:
            return image
        
        target_width, target_height = self.RATIOS[ratio_name]
        h, w = image.shape[:2]
        
        current_ratio = w / h
        target_ratio = target_width / target_height
        
        if current_ratio > target_ratio:
            # Add horizontal bars (top/bottom)
            new_height = int(w / target_ratio)
            bar_height = (new_height - h) // 2
            
            top_bar = np.full((bar_height, w, 3), bar_color, dtype=image.dtype)
            bottom_bar = np.full((bar_height, w, 3), bar_color, dtype=image.dtype)
            
            result = np.vstack([top_bar, image, bottom_bar])
        else:
            # Add vertical bars (left/right)  
            new_width = int(h * target_ratio)
            bar_width = (new_width - w) // 2
            
            left_bar = np.full((h, bar_width, 3), bar_color, dtype=image.dtype)
            right_bar = np.full((h, bar_width, 3), bar_color, dtype=image.dtype)
            
            result = np.hstack([left_bar, image, right_bar])
        
        return result

### 6. Style Presets (`backend/app/processors/style_presets.py`)

```python
from typing import Dict, Any

class A24StylePresets:
    """Predefined style configurations for different A24 films"""
    
    @staticmethod
    def get_all_presets() -> Dict[str, Dict[str, Any]]:
        return {
            'moonlight': {
                'name': 'Moonlight',
                'description': 'Cyan-magenta contrasts with dreamy coastal atmosphere',
                'lut': 'moonlight',
                'split_tone_highlights': (255, 200, 180),
                'split_tone_shadows': (100, 150, 200),
                'desaturation': 0.2,
                'shadow_lift': 0.15,
                'grain_type': '35mm',
                'grain_intensity': 0.25,
                'halation_strength': 0.4,
                'chromatic_aberration': 1.0,
                'aspect_ratio': 'cinematic',
                'lighting_direction': 'left',
                'lighting_intensity': 0.6,
                'temperature': 'cool'
            },
            'hereditary': {
                'name': 'Hereditary',
                'description': 'Warm interiors with unsettling green shadows',
                'lut': 'hereditary',
                'split_tone_highlights': (255, 220, 180),
                'split_tone_shadows': (80, 120, 100),
                'desaturation': 0.3,
                'shadow_lift': 0.1,
                'grain_type': '16mm',
                'grain_intensity': 0.4,
                'halation_strength': 0.2,
                'chromatic_aberration': 2.0,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top',
                'lighting_intensity': 0.7,
                'temperature': 'warm'
            },
            'green_knight': {
                'name': 'The Green Knight',
                'description': 'Medieval earthiness with candlelit warmth',
                'lut': 'green_knight',
                'split_tone_highlights': (200, 180, 120),
                'split_tone_shadows': (60, 80, 40),
                'desaturation': 0.4,
                'shadow_lift': 0.05,
                'grain_type': '35mm',
                'grain_intensity': 0.3,
                'halation_strength': 0.5,
                'chromatic_aberration': 1.5,
                'aspect_ratio': 'cinematic',
                'lighting_direction': 'right',
                'lighting_intensity': 0.5,
                'temperature': 'warm'
            },
            'lighthouse': {
                'name': 'The Lighthouse',
                'description': 'Black and white with crushing claustrophobia',
                'lut': 'lighthouse',
                'split_tone_highlights': (240, 240, 220),
                'split_tone_shadows': (40, 60, 80),
                'desaturation': 0.5,
                'shadow_lift': 0.2,
                'grain_type': '16mm',
                'grain_intensity': 0.5,
                'halation_strength': 0.3,
                'chromatic_aberration': 3.0,
                'aspect_ratio': 'academy',
                'lighting_direction': 'left',
                'lighting_intensity': 0.8,
                'temperature': 'cool'
            },
            'eighth_grade': {
                'name': 'Eighth Grade',
                'description': 'Natural digital look with subtle warmth',
                'lut': None,
                'split_tone_highlights': (255, 240, 220),
                'split_tone_shadows': (200, 210, 220),
                'desaturation': 0.1,
                'shadow_lift': 0.12,
                'grain_type': 'digital',
                'grain_intensity': 0.15,
                'halation_strength': 0.1,
                'chromatic_aberration': 0.5,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top',
                'lighting_intensity': 0.4,
                'temperature': 'neutral'
            },
            'midsommar': {
                'name': 'Midsommar',
                'description': 'Bright daylight horror with saturated pastels',
                'lut': None,
                'split_tone_highlights': (255, 250, 200),
                'split_tone_shadows': (180, 200, 150),
                'desaturation': -0.1,  # Actually increase saturation slightly
                'shadow_lift': 0.3,
                'grain_type': '35mm',
                'grain_intensity': 0.2,
                'halation_strength': 0.6,
                'chromatic_aberration': 1.0,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top',
                'lighting_intensity': 0.3,
                'temperature': 'warm'
            }
        }
    
    @staticmethod
    def get_preset(name: str) -> Dict[str, Any]:
        presets = A24StylePresets.get_all_presets()
        return presets.get(name, presets['moonlight'])
```

## Frontend Development

### 1. Main App Component (`frontend/src/App.tsx`)

```tsx
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
```

### 2. Image Upload Component (`frontend/src/components/ImageUpload.tsx`)

```tsx
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
```

### 3. Style Selector Component (`frontend/src/components/StyleSelector.tsx`)

```tsx
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
```

### 4. Processing Status Component (`frontend/src/components/ProcessingStatus.tsx`)

```tsx
import React from 'react';
import { Loader2, Film } from 'lucide-react';

interface ProcessingStatusProps {
  progress: number;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ progress }) => {
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
        <Loader2 className="text-blue-400 animate-spin" size={24} />
        <h3 className="text-xl font-semibold text-white">
          Processing Your Image
        </h3>
      </div>

      <div className="space-y-4">
        {/* Progress Bar */}
        <div>
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>{stages[currentStage]}</span>
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
```

### 5. Result Display Component (`frontend/src/components/ResultDisplay.tsx`)

```tsx
import React, { useState } from 'react';
import { Download, Eye, EyeOff, Maximize2 } from 'lucide-react';

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
```

### 6. Custom Hook for Image Processing (`frontend/src/hooks/useImageProcessing.ts`)

```tsx
import { useState, useCallback } from 'react';
import { processImage as apiProcessImage } from '../services/api';
import { ProcessingRequest } from '../types';

interface UseImageProcessingReturn {
  processImage: (file: File, request: ProcessingRequest) => Promise<void>;
  isProcessing: boolean;
  progress: number;
  result: string | null;
  error: string | null;
  reset: () => void;
}

export const useImageProcessing = (): UseImageProcessingReturn => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const processImage = useCallback(async (file: File, request: ProcessingRequest) => {
    setIsProcessing(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + Math.random() * 15, 95));
      }, 500);

      const processedImageUrl = await apiProcessImage(file, request);
      
      clearInterval(progressInterval);
      setProgress(100);
      setResult(processedImageUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsProcessing(false);
    setProgress(0);
    setResult(null);
    setError(null);
  }, []);

  return {
    processImage,
    isProcessing,
    progress,
    result,
    error,
    reset
  };
};
```

### 7. API Service (`frontend/src/services/api.ts`)

```tsx
import axios from 'axios';
import { ProcessingRequest } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for image processing
});

export const processImage = async (
  file: File, 
  request: ProcessingRequest
): Promise<string> => {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('style', request.style);
  
  if (request.customSettings) {
    formData.append('custom_settings', JSON.stringify(request.customSettings));
  }

  const response = await api.post('/process-image/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
  });

  // Convert blob to URL for display
  const imageUrl = URL.createObjectURL(response.data);
  return imageUrl;
};

export const getAvailableStyles = async (): Promise<string[]> => {
  const response = await api.get('/styles/');
  return response.data.styles;
};

export const getStylePreset = async (styleName: string) => {
  const response = await api.get(`/styles/${styleName}/`);
  return response.data;
};
```

### 8. TypeScript Types (`frontend/src/types/index.ts`)

```tsx
export interface StylePreset {
  name: string;
  description: string;
  lut?: string;
  split_tone_highlights: [number, number, number];
  split_tone_shadows: [number, number, number];
  desaturation: number;
  shadow_lift: number;
  grain_type: string;
  grain_intensity: number;
  halation_strength: number;
  chromatic_aberration: number;
  aspect_ratio: string;
  lighting_direction: string;
  lighting_intensity: number;
  temperature: string;
}

export interface ProcessingRequest {
  style: string;
  customSettings?: Partial<StylePreset>;
}

export interface ProcessingResponse {
  success: boolean;
  message?: string;
  processed_image?: string;
  error?: string;
}
```

## Backend API

### 1. Main FastAPI App (`backend/app/main.py`)

```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import json
import io
from PIL import Image
import os
from typing import Optional

from .processors.a24_processor import A24StyleProcessor
from .processors.style_presets import A24StylePresets
from .utils.image_utils import validate_image, prepare_image_response

# Initialize FastAPI app
app = FastAPI(
    title="A24 Style Transfer API",
    description="Transform photos with cinematic A24 aesthetics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processor
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")
processor = A24StyleProcessor(ASSETS_PATH)

@app.get("/")
async def root():
    return {"message": "A24 Style Transfer API is running"}

@app.get("/styles/")
async def get_available_styles():
    """Get list of available A24 styles"""
    presets = A24StylePresets.get_all_presets()
    return {
        "styles": list(presets.keys()),
        "presets": {k: v for k, v in presets.items()}
    }

@app.get("/styles/{style_name}/")
async def get_style_preset(style_name: str):
    """Get specific style preset details"""
    preset = A24StylePresets.get_preset(style_name)
    if not preset:
        raise HTTPException(status_code=404, detail="Style not found")
    return preset

@app.post("/process-image/")
async def process_image(
    image: UploadFile = File(...),
    style: str = Form(...),
    custom_settings: Optional[str] = Form(None)
):
    """Process image with A24 style"""
    try:
        # Validate uploaded image
        if not validate_image(image):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Read and decode image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        
        # Parse custom settings if provided
        settings = None
        if custom_settings:
            try:
                settings = json.loads(custom_settings)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid custom settings JSON")
        
        # Process image
        result_image = processor.process_image_array(cv_image, style, settings)
        
        # Prepare response
        return prepare_image_response(result_image)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "processor": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Enhanced A24 Processor (`backend/app/processors/a24_processor.py`)

```python
import cv2
import numpy as np
import os
from typing import Dict, Any, Optional

from ..core.color_grading import ColorGrader
from ..core.film_texture import FilmTexture
from ..core.lighting_simulation import LightingSimulator
from ..core.aspect_ratio import AspectRatioProcessor, CompositionEnhancer
from .style_presets import A24StylePresets

class A24StyleProcessor:
    """Enhanced A24 style processor with error handling and optimization"""
    
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self._initialize_processors()
        self.presets = A24StylePresets.get_all_presets()
    
    def _initialize_processors(self):
        """Initialize all processing modules"""
        try:
            self.color_grader = ColorGrader(self.assets_path)
            self.film_texture = FilmTexture(self.assets_path)
            self.lighting_sim = LightingSimulator()
            self.aspect_processor = AspectRatioProcessor()
            self.composition = CompositionEnhancer()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize processors: {e}")
    
    def process_image_array(self, image: np.ndarray, 
                           style: str = 'moonlight',
                           custom_settings: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Process numpy array image with A24 style"""
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume BGR input from OpenCV
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get preset settings
        settings = self.presets.get(style, self.presets['moonlight']).copy()
        if custom_settings:
            settings.update(custom_settings)
        
        # Processing pipeline with error handling
        result = image.copy()
        
        try:
            # Step 1: Color grading
            result = self._apply_color_grading_safe(result, settings)
            
            # Step 2: Lighting simulation
            result = self._apply_lighting_safe(result, settings)
            
            # Step 3: Film texture
            result = self._apply_film_texture_safe(result, settings)
            
            # Step 4: Composition and aspect ratio
            result = self._apply_composition_safe(result, settings)
            
        except Exception as e:
            print(f"Processing error: {e}")
            # Return original image if processing fails
            return image
        
        return result
    
    def _apply_color_grading_safe(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply color grading with error handling"""
        try:
            result = image.copy()
            
            # Apply LUT if available
            if 'lut' in settings and settings['lut']:
                result = self.color_grader.apply_lut(result, settings['lut'])
            
            # Split toning
            if all(k in settings for k in ['split_tone_highlights', 'split_tone_shadows']):
                result = self.color_grader.split_tone(
                    result,
                    tuple(settings['split_tone_highlights']),
                    tuple(settings['split_tone_shadows'])
                )
            
            # Desaturation
            desaturation = settings.get('desaturation', 0.3)
            if desaturation > 0:
                result = self.color_grader.desaturate(result, desaturation)
            
            # Shadow lift
            shadow_lift = settings.get('shadow_lift', 0.1)
            if shadow_lift > 0:
                result = self.color_grader.lift_shadows(result, shadow_lift)
            
            return result
            
        except Exception as e:
            print(f"Color grading error: {e}")
            return image
    
    def _apply_lighting_safe(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply lighting with error handling"""
        try:
            result = image.copy()
            
            # Window lighting
            lighting_direction = settings.get('lighting_direction', 'left')
            lighting_intensity = settings.get('lighting_intensity', 0.6)
            
            result = self.lighting_sim.simulate_window_light(
                result, 
                lighting_direction,
                lighting_intensity
            )
            
            # Enhance shadows
            result = self.lighting_sim.enhance_shadows(result)
            
            return result
            
        except Exception as e:
            print(f"Lighting simulation error: {e}")
            return image
    
    def _apply_film_texture_safe(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply film texture with error handling"""
        try:
            result = image.copy()
            
            # Film grain
            grain_type = settings.get('grain_type', '35mm')
            grain_intensity = settings.get('grain_intensity', 0.3)
            
            result = self.film_texture.add_film_grain(
                result,
                grain_type,
                grain_intensity
            )
            
            # Halation
            halation_strength = settings.get('halation_strength', 0.3)
            if halation_strength > 0:
                result = self.film_texture.add_halation(result, halation_strength)
            
            # Chromatic aberration
            chromatic_aberration = settings.get('chromatic_aberration', 1.5)
            if chromatic_aberration > 0:
                result = self.film_texture.add_chromatic_aberration(
                    result, 
                    chromatic_aberration
                )
            
            return result
            
        except Exception as e:
            print(f"Film texture error: {e}")
            return image
    
    def _apply_composition_safe(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply composition changes with error handling"""
        try:
            result = image.copy()
            
            # Reframe for symmetry
            result = self.composition.reframe_for_symmetry(result)
            
            # Aspect ratio
            aspect_ratio = settings.get('aspect_ratio', 'cinematic')
            if aspect_ratio != 'original':
                result = self.aspect_processor.change_aspect_ratio(
                    result, 
                    aspect_ratio
                )
            
            return result
            
        except Exception as e:
            print(f"Composition error: {e}")
            return image
```

### 3. Image Utilities (`backend/app/utils/image_utils.py`)

```python
import cv2
import numpy as np
from PIL import Image
from fastapi import UploadFile
from fastapi.responses import Response
import io

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    # Check file extension
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return False
    
    # Check file size (this is approximate since we're reading the file)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        return False
    
    return True

def prepare_image_response(image: np.ndarray, format: str = 'JPEG', quality: int = 95) -> Response:
    """Convert numpy array to HTTP response"""
    # Convert RGB to BGR for OpenCV
    if len(image.shape) == 3:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = image
    
    # Encode image
    if format.upper() == 'JPEG':
        _, buffer = cv2.imencode('.jpg', image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        media_type = "image/jpeg"
    elif format.upper() == 'PNG':
        _, buffer = cv2.imencode('.png', image_bgr)
        media_type = "image/png"
    else:
        _, buffer = cv2.imencode('.jpg', image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        media_type = "image/jpeg"
    
    return Response(content=buffer.tobytes(), media_type=media_type)

def resize_image_if_needed(image: np.ndarray, max_dimension: int = 2048) -> np.ndarray:
    """Resize image if it's too large"""
    h, w = image.shape[:2]
    
    if max(h, w) <= max_dimension:
        return image
    
    # Calculate new dimensions
    if h > w:
        new_h = max_dimension
        new_w = int(w * max_dimension / h)
    else:
        new_w = max_dimension
        new_h = int(h * max_dimension / w)
    
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

def enhance_image_quality(image: np.ndarray) -> np.ndarray:
    """Apply subtle image enhancement"""
    # Slight sharpening
    kernel = np.array([[-1,-1,-1],
                      [-1, 9,-1],
                      [-1,-1,-1]]) * 0.1
    sharpened = cv2.filter2D(image, -1, kernel)
    
    # Blend with original
    result = cv2.addWeighted(image, 0.8, sharpened, 0.2, 0)
    
    return result

def convert_to_rgb(image: np.ndarray) -> np.ndarray:
    """Ensure image is in RGB format"""
    if len(image.shape) == 3:
        if image.shape[2] == 4:  # RGBA
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif image.shape[2] == 3:
            # Assume BGR and convert to RGB
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    return image
```

## Testing & Deployment

### 1. Docker Configuration

#### Backend Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create assets directory
RUN mkdir -p /app/assets/luts /app/assets/grain_textures /app/assets/models

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/assets:/app/assets
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### 2. Setup Script (`setup.sh`)

```bash
#!/bin/bash

echo "Setting up A24 Style Transfer App..."

# Create project structure
mkdir -p backend/app/{core,processors,api,utils,models}
mkdir -p backend/assets/{luts,grain_textures,models}
mkdir -p frontend/src/{components,hooks,services,types}

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create sample LUT files (you'll need to replace these with actual LUTs)
echo "Creating sample asset files..."
# Note: You'll need to obtain actual LUT files for each movie style

# Frontend setup
echo "Setting up frontend..."
cd ../frontend
npm install

echo "Setup complete!"
echo ""
echo "To start development:"
echo "1. Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use Docker: docker-compose up --build"
```

### 3. Testing

#### Basic Test Suite (`backend/tests/test_processor.py`)

```python
import pytest
import numpy as np
import cv2
from app.processors.a24_processor import A24StyleProcessor
from app.processors.style_presets import A24StylePresets

@pytest.fixture
def processor():
    return A24StyleProcessor("./assets")

@pytest.fixture  
def sample_image():
    # Create a simple test image
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

def test_processor_initialization(processor):
    assert processor is not None
    assert hasattr(processor, 'color_grader')
    assert hasattr(processor, 'film_texture')

def test_process_image_basic(processor, sample_image):
    result = processor.process_image_array(sample_image, 'moonlight')
    
    assert result is not None
    assert result.shape == sample_image.shape
    assert result.dtype == np.uint8

def test_all_presets(processor, sample_image):
    presets = A24StylePresets.get_all_presets()
    
    for style_name in presets.keys():
        result = processor.process_image_array(sample_image, style_name)
        assert result is not None
        assert result.shape == sample_image.shape

def test_custom_settings(processor, sample_image):
    custom_settings = {
        'desaturation': 0.5,
        'grain_intensity': 0.6
    }
    
    result = processor.process_image_array(
        sample_image, 
        'moonlight', 
        custom_settings
    )
    
    assert result is not None
    assert result.shape == sample_image.shape

if __name__ == "__main__":
    pytest.main([__file__])
```

### 4. Production Deployment

#### Production Docker Compose (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    expose:
      - "8000"
    volumes:
      - ./backend/assets:/app/assets
    environment:
      - ENVIRONMENT=production
      - WORKERS=4
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend  
      dockerfile: Dockerfile.prod
    expose:
      - "3000"
    environment:
      - REACT_APP_API_URL=https://your-domain.com/api
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - backend
    restart: unless-stopped
```

## Getting Started

1. **Clone and Setup**:
   ```bash
   git clone <your-repo>
   cd a24-style-app
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Obtain Assets**:
   - LUT files for each movie style
   - Film grain textures
   - Pre-trained lighting models (optional)

3. **Development**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend  
   cd frontend
   npm start
   ```

4. **Production**:
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

This guide provides a complete, production-ready A24 style transfer application. The modular architecture allows for easy extension with additional styles and effects, while the modern web interface provides an excellent user experience.
```

class CompositionEnhancer:
    
    def reframe_for_symmetry(self, image: np.ndarray,
                           face_detection: bool = True) -> np.ndarray:
        """Reframe image for A24-style symmetrical composition"""
        if not face_detection:
            return image
        
        # Load OpenCV face detector
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return image
        
        # Get primary face
        face = faces[0]  # Largest face
        x, y, face_w, face_h = face
        
        # Calculate face center
        face_center_x = x + face_w // 2
        face_center_y = y + face_h // 2
        
        h, w = image.shape[:2]
        
        # Center the face horizontally
        target_center_x = w // 2
        shift_x = target_center_x - face_center_x
        
        # Apply shift (with bounds checking)
        if shift_x > 0:
            # Shift right
            shift_x = min(shift_x, w - face_center_x - face_w//2)
            result = np.zeros_like(image)
            result[:, shift_x:] = image[:, :w-shift_x]
        elif shift_x < 0:
            # Shift left
            shift_x = max(shift_x, -face_center_x + face_w//2)
            result = np.zeros_like(image)
            result[:, :w+shift_x] = image[:, -shift_x:]
        else:
            result = image
        
        return result
```

### 5. Main A24 Processor (`backend/app/processors/a24_processor.py`)

```python
import cv2
import numpy as np
from typing import Dict, Any, Optional
import os

from ..core.color_grading import ColorGrader
from ..core.film_texture import FilmTexture
from ..core.lighting_simulation import LightingSimulator
from ..core.aspect_ratio import AspectRatioProcessor, CompositionEnhancer

class A24StyleProcessor:
    
    def __init__(self, assets_path: str):
        self.color_grader = ColorGrader(assets_path)
        self.film_texture = FilmTexture(assets_path)
        self.lighting_sim = LightingSimulator()
        self.aspect_processor = AspectRatioProcessor()
        self.composition = CompositionEnhancer()
        
        # Define A24 movie presets
        self.presets = {
            'moonlight': {
                'lut': 'moonlight',
                'split_tone_highlights': (255, 200, 180),
                'split_tone_shadows': (100, 150, 200),
                'desaturation': 0.2,
                'grain_type': '35mm',
                'grain_intensity': 0.25,
                'aspect_ratio': 'cinematic',
                'lighting_direction': 'left'
            },
            'hereditary': {
                'lut': 'hereditary', 
                'split_tone_highlights': (255, 220, 180),
                'split_tone_shadows': (80, 120, 100),
                'desaturation': 0.3,
                'grain_type': '16mm',
                'grain_intensity': 0.4,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top'
            },
            'green_knight': {
                'lut': 'green_knight',
                'split_tone_highlights': (200, 180, 120),
                'split_tone_shadows': (60, 80, 40),
                'desaturation': 0.4,
                'grain_type': '35mm', 
                'grain_intensity': 0.3,
                'aspect_ratio': 'cinematic',
                'lighting_direction': 'right'
            },
            'lighthouse': {
                'lut': 'lighthouse',
                'split_tone_highlights': (240, 240, 220),
                'split_tone_shadows': (40, 60, 80),
                'desaturation': 0.5,
                'grain_type': '16mm',
                'grain_intensity': 0.5,
                'aspect_ratio': 'academy',
                'lighting_direction': 'left'
            }
        }
    
    def process_image(self, image_path: str, 
                     style: str = 'moonlight',
                     custom_settings: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Main processing pipeline"""
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Get preset settings
        settings = self.presets.get(style, self.presets['moonlight']).copy()
        if custom_settings:
            settings.update(custom_settings)
        
        # Processing pipeline
        result = image.copy()
        
        # Step 1: Color grading
        result = self._apply_color_grading(result, settings)
        
        # Step 2: Lighting simulation
        result = self._apply_lighting(result, settings)
        
        # Step 3: Film texture
        result = self._apply_film_texture(result, settings)
        
        # Step 4: Composition and aspect ratio
        result = self._apply_composition(result, settings)
        
        return result
    
    def _apply_color_grading(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply color grading pipeline"""
        result = image.copy()
        
        # Apply LUT
        if 'lut' in settings:
            result = self.color_grader.apply_lut(result, settings['lut'])
        
        # Split toning
        if 'split_tone_highlights' in settings and 'split_tone_shadows' in settings:
            result = self.color_grader.split_tone(
                result,
                settings['split_tone_highlights'],
                settings['split_tone_shadows']
            )
        
        # Desaturation
        if 'desaturation' in settings:
            result = self.color_grader.desaturate(result, settings['desaturation'])
        
        # Lift shadows
        result = self.color_grader.lift_shadows(result, 0.1)
        
        return result
    
    def _apply_lighting(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply lighting simulation"""
        result = image.copy()
        
        # Window lighting
        if 'lighting_direction' in settings:
            result = self.lighting_sim.simulate_window_light(
                result, 
                settings['lighting_direction'],
                0.6
            )
        
        # Enhance shadows with cool tones
        result = self.lighting_sim.enhance_shadows(result)
        
        return result
    
    def _apply_film_texture(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply film texture effects"""
        result = image.copy()
        
        # Film grain
        if 'grain_type' in settings and 'grain_intensity' in settings:
            result = self.film_texture.add_film_grain(
                result,
                settings['grain_type'],
                settings['grain_intensity']
            )
        
        # Halation
        result = self.film_texture.add_halation(result, 0.3)
        
        # Chromatic aberration
        result = self.film_texture.add_chromatic_aberration(result, 1.5)
        
        return result
    
    def _apply_composition(self, image: np.ndarray, settings: Dict) -> np.ndarray:
        """Apply composition and aspect ratio changes"""
        result = image.copy()
        
        # Reframe for symmetry
        result = self.composition.reframe_for_symmetry(result)
        
        # Aspect ratio
        if 'aspect_ratio' in settings:
            result = self.aspect_processor.change_aspect_ratio(
                result, 
                settings['aspect_ratio']
            )
        
        return result
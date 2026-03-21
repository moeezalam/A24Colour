import cv2
import numpy as np
from PIL import Image
import random
from typing import Tuple
import os

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
            else:
                # Create procedural grain if file doesn't exist
                textures[grain_type] = self._create_procedural_grain(grain_type)
        return textures
    
    def _create_procedural_grain(self, grain_type: str) -> np.ndarray:
        """Create procedural grain texture"""
        size = 512
        if grain_type == '16mm':
            # Coarser grain
            noise = np.random.normal(128, 40, (size, size))
        elif grain_type == '35mm':
            # Medium grain
            noise = np.random.normal(128, 25, (size, size))
        else:  # digital
            # Fine grain
            noise = np.random.normal(128, 15, (size, size))
        
        return np.clip(noise, 0, 255).astype(np.uint8)
    
    def add_film_grain(self, image: np.ndarray, grain_type: str = '35mm', 
                      intensity: float = 0.3) -> np.ndarray:
        """Add film grain texture"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        if grain_type not in self.grain_textures:
            # Generate procedural grain if texture not available
            return self._add_procedural_grain(image, intensity)
        
        grain_texture = self.grain_textures[grain_type]
        if grain_texture is None:
            return self._add_procedural_grain(image, intensity)
        
        h, w = image.shape[:2]
        
        # Resize grain texture to match image
        grain_resized = cv2.resize(grain_texture, (w, h))
        
        # Normalize grain to [-1, 1]
        grain_normalized = (grain_resized.astype(np.float32) - 128) / 128
        
        # Apply grain to each channel safely
        result = image.copy().astype(np.float32)
        for i in range(min(3, image.shape[2])):  # Ensure we don't exceed channel count
            result[:,:,i] += grain_normalized * intensity * 30
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _add_procedural_grain(self, image: np.ndarray, intensity: float) -> np.ndarray:
        """Generate procedural grain"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        h, w = image.shape[:2]
        
        # Generate random noise
        noise = np.random.normal(0, 1, (h, w)) * intensity * 25
        
        # Apply to all channels safely
        result = image.copy().astype(np.float32)
        for i in range(min(3, image.shape[2])):  # Ensure we don't exceed channel count
            result[:,:,i] += noise
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def add_halation(self, image: np.ndarray, strength: float = 0.5) -> np.ndarray:
        """Add halation/bloom effect around highlights"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        try:
            # Find bright areas
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
            
            # Create glow effect
            glow = cv2.GaussianBlur(bright_mask, (21, 21), 8)
            glow = glow.astype(np.float32) / 255.0 * strength
            
            # Apply glow to original image safely
            result = image.copy().astype(np.float32)
            for i in range(min(3, image.shape[2])):
                result[:,:,i] = result[:,:,i] + glow * 50
            
            return np.clip(result, 0, 255).astype(np.uint8)
        except Exception as e:
            print(f"Halation error: {e}")
            return image
    
    def add_chromatic_aberration(self, image: np.ndarray, 
                                strength: float = 2.0) -> np.ndarray:
        """Add subtle chromatic aberration"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        try:
            h, w = image.shape[:2]
            
            # Create displacement maps
            shift_x = int(strength)
            shift_y = int(strength * 0.3)
            
            # Split into channels - Note: OpenCV uses BGR, but we're working with RGB
            r, g, b = cv2.split(image)  # Split RGB channels
            
            # Shift red channel
            M_r = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            r_shifted = cv2.warpAffine(r, M_r, (w, h), borderMode=cv2.BORDER_REFLECT)
            
            # Shift blue channel (opposite direction)
            M_b = np.float32([[1, 0, -shift_x], [0, 1, -shift_y]])
            b_shifted = cv2.warpAffine(b, M_b, (w, h), borderMode=cv2.BORDER_REFLECT)
            
            # Recombine - maintain RGB order
            return cv2.merge([r_shifted, g, b_shifted])
        except Exception as e:
            print(f"Chromatic aberration error: {e}")
            return image
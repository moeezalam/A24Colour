import cv2
import numpy as np
from typing import Tuple, Optional, Dict
import os

class ColorGrader:
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self.luts = self._load_luts()
    
    def _load_luts(self) -> Dict[str, Optional[np.ndarray]]:
        """Load all A24 style LUTs - placeholder implementation"""
        lut_files = {
            'moonlight': 'moonlight.cube',
            'hereditary': 'hereditary.cube', 
            'green_knight': 'green_knight.cube',
            'lighthouse': 'lighthouse.cube'
        }
        
        luts = {}
        for style, filename in lut_files.items():
            path = os.path.join(self.assets_path, 'luts', filename)
            # For now, we'll use procedural LUTs since actual .cube files aren't available
            luts[style] = self._create_procedural_lut(style)
        return luts
    
    def _create_procedural_lut(self, style: str) -> np.ndarray:
        """Create procedural LUT based on style"""
        # Create a basic 3D LUT (simplified version)
        size = 32
        lut = np.zeros((size, size, size, 3), dtype=np.float32)
        
        for r in range(size):
            for g in range(size):
                for b in range(size):
                    # Normalize to 0-1
                    nr, ng, nb = r/size, g/size, b/size
                    
                    if style == 'moonlight':
                        # Cyan-magenta look
                        nr = nr * 0.9 + 0.05
                        ng = ng * 1.1
                        nb = nb * 1.2 + 0.1
                    elif style == 'hereditary':
                        # Warm-green look
                        nr = nr * 1.2 + 0.1
                        ng = ng * 1.0 + 0.05
                        nb = nb * 0.8
                    elif style == 'green_knight':
                        # Medieval earthy look
                        nr = nr * 1.1 + 0.05
                        ng = ng * 1.0 + 0.1
                        nb = nb * 0.7
                    elif style == 'lighthouse':
                        # Desaturated monochrome look
                        avg = (nr + ng + nb) / 3
                        nr = avg * 1.1
                        ng = avg * 1.05
                        nb = avg * 0.95
                    
                    lut[r, g, b] = [nr, ng, nb]
        
        return lut
    
    def apply_lut(self, image: np.ndarray, style: str, strength: float = 1.0) -> np.ndarray:
        """Apply LUT with specified strength"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if style not in self.luts or self.luts[style] is None:
            return image
        
        # Ensure we have a 3-channel image
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        # Make a copy and convert to float32
        result = image.copy().astype(np.float32) / 255.0
        
        # Apply style-specific color grading
        if style == 'moonlight':
            # Cyan-magenta grading
            result[:,:,0] = np.clip(result[:,:,0] * 0.9 + 0.05, 0, 1)  # R
            result[:,:,1] = np.clip(result[:,:,1] * 1.1, 0, 1)          # G
            result[:,:,2] = np.clip(result[:,:,2] * 1.2 + 0.1, 0, 1)   # B
        elif style == 'hereditary':
            # Warm-green grading
            result[:,:,0] = np.clip(result[:,:,0] * 1.2 + 0.1, 0, 1)
            result[:,:,1] = np.clip(result[:,:,1] * 1.0 + 0.05, 0, 1)
            result[:,:,2] = np.clip(result[:,:,2] * 0.8, 0, 1)
        elif style == 'green_knight':
            # Medieval earthy grading
            result[:,:,0] = np.clip(result[:,:,0] * 1.1 + 0.05, 0, 1)
            result[:,:,1] = np.clip(result[:,:,1] * 1.0 + 0.1, 0, 1)
            result[:,:,2] = np.clip(result[:,:,2] * 0.7, 0, 1)
        elif style == 'lighthouse':
            # Desaturated monochrome - FIX: Properly handle grayscale conversion
            gray = np.dot(result, [0.299, 0.587, 0.114])
            # Ensure gray maintains proper dimensions
            result[:,:,0] = np.clip(gray * 1.1, 0, 1)
            result[:,:,1] = np.clip(gray * 1.05, 0, 1)
            result[:,:,2] = np.clip(gray * 0.95, 0, 1)
        
        # Blend with original based on strength
        original_float = image.astype(np.float32) / 255.0
        blended = original_float * (1 - strength) + result * strength
        
        # Convert back to uint8 and ensure valid range
        return (np.clip(blended, 0, 1) * 255).astype(np.uint8)
    
    def split_tone(self, image: np.ndarray, highlight_color: Tuple[int, int, int], 
                   shadow_color: Tuple[int, int, int], balance: float = 0.0) -> np.ndarray:
        """Apply split toning (warm highlights, cool shadows)"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        try:
            # Convert to LAB color space for better luminance separation
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
                if i < 3:  # Ensure we don't exceed channel count
                    result[:,:,i] += highlight_mask * h_color * 0.3
                    result[:,:,i] += shadow_mask * s_color * 0.3
            
            return np.clip(result, 0, 255).astype(np.uint8)
        except Exception as e:
            print(f"Split tone error: {e}")
            return image
    
    def desaturate(self, image: np.ndarray, amount: float = 0.3) -> np.ndarray:
        """Reduce saturation for muted A24 look"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        try:
            # Convert to HSV and reduce saturation
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            hsv = hsv.astype(np.float32)
            hsv[:,:,1] = hsv[:,:,1] * (1 - amount)
            hsv = np.clip(hsv, 0, 255).astype(np.uint8)
            result = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            return result
        except Exception as e:
            print(f"Desaturation error: {e}")
            return image
    
    def lift_shadows(self, image: np.ndarray, lift: float = 0.1) -> np.ndarray:
        """Lift shadows without crushing blacks"""
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        try:
            img_float = image.astype(np.float32) / 255.0
            
            # Create shadow mask (non-linear) - apply to luminance
            luminance = np.dot(img_float, [0.299, 0.587, 0.114])
            shadow_mask = 1 - np.power(luminance, 0.5)
            
            # Expand shadow mask to 3 channels
            shadow_mask = np.expand_dims(shadow_mask, axis=2)
            shadow_mask = np.repeat(shadow_mask, 3, axis=2)
            
            # Lift shadows
            lifted = img_float + shadow_mask * lift
            
            return (np.clip(lifted, 0, 1) * 255).astype(np.uint8)
        except Exception as e:
            print(f"Shadow lift error: {e}")
            return image
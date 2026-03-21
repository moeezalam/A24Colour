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
        # Validate input
        if image is None or image.size == 0:
            return image
        
        if ratio_name not in self.RATIOS:
            return image
        
        if len(image.shape) != 3 or image.shape[2] != 3:
            return image
        
        try:
            target_width, target_height = self.RATIOS[ratio_name]
            h, w = image.shape[:2]
            
            current_ratio = w / h
            target_ratio = target_width / target_height
            
            # If ratios are very close, don't crop
            if abs(current_ratio - target_ratio) < 0.05:
                return image
            
            if current_ratio > target_ratio:
                # Image is wider, crop width
                new_width = int(h * target_ratio)
                new_width = max(1, min(new_width, w))  # Ensure valid width
                
                if crop_position == 'center':
                    start_x = max(0, (w - new_width) // 2)
                elif crop_position == 'left':
                    start_x = 0
                else:  # right
                    start_x = max(0, w - new_width)
                
                end_x = min(w, start_x + new_width)
                cropped = image[:, start_x:end_x]
            else:
                # Image is taller, crop height
                new_height = int(w / target_ratio)
                new_height = max(1, min(new_height, h))  # Ensure valid height
                
                if crop_position == 'center':
                    start_y = max(0, (h - new_height) // 2)
                elif crop_position == 'top':
                    start_y = 0
                else:  # bottom
                    start_y = max(0, h - new_height)
                
                end_y = min(h, start_y + new_height)
                cropped = image[start_y:end_y, :]
            
            # Validate result
            if cropped.size == 0:
                print(f"Warning: Aspect ratio crop resulted in empty image, returning original")
                return image
            
            return cropped
            
        except Exception as e:
            print(f"Aspect ratio error: {e}")
            return image
    
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

class CompositionEnhancer:
    
    def reframe_for_symmetry(self, image: np.ndarray,
                           face_detection: bool = False) -> np.ndarray:
        """Reframe image for A24-style symmetrical composition"""
        # DISABLED: This function was causing black regions in images
        # Face detection and reframing can cause issues with image boundaries
        # For now, we'll skip this step to ensure image integrity
        return image
        
        # Original implementation kept for reference but disabled
        if not face_detection:
            return image
        
        try:
            # Validate input
            if image is None or image.size == 0:
                return image
            
            if len(image.shape) != 3 or image.shape[2] != 3:
                return image
            
            # Load OpenCV face detector
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return image
            
            # Get primary face (largest)
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, face_w, face_h = largest_face
            
            # Calculate face center
            face_center_x = x + face_w // 2
            
            h, w = image.shape[:2]
            
            # Only apply small adjustments to avoid black regions
            target_center_x = w // 2
            shift_x = target_center_x - face_center_x
            
            # Limit shift to prevent black regions
            max_shift = min(w // 4, 50)  # Limit to 25% of width or 50 pixels
            shift_x = np.clip(shift_x, -max_shift, max_shift)
            
            if abs(shift_x) < 10:  # Skip tiny adjustments
                return image
            
            # Apply safe shift using cv2.warpAffine to avoid black regions
            M = np.float32([[1, 0, shift_x], [0, 1, 0]])
            result = cv2.warpAffine(image, M, (w, h), borderMode=cv2.BORDER_REFLECT)
            
            return result
            
        except Exception as e:
            print(f"Face reframing error: {e}")
            # If face detection fails, return original image
            return image
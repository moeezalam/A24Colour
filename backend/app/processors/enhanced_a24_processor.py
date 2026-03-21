import cv2
import numpy as np
import os
from typing import Dict, Any, Optional
import time
import logging
from scipy import ndimage
from skimage import exposure, filters

logger = logging.getLogger(__name__)

class EnhancedA24StyleProcessor:
    """Enhanced A24 style processor with advanced image processing techniques"""
    
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self.reference_styles = self._load_reference_styles()
        logger.info("Enhanced A24 Style Processor initialized")
    
    def _load_reference_styles(self):
        """Load reference style images for color matching"""
        styles = {}
        style_files = {
            'moonlight': 'moonlight_reference.jpg',
            'hereditary': 'hereditary_reference.jpg',
            'green_knight': 'green_knight_reference.jpg',
            'lighthouse': 'lighthouse_reference.jpg',
            'eighth_grade': 'eighth_grade_reference.jpg',
            'midsommar': 'midsommar_reference.jpg'
        }
        
        reference_path = os.path.join(self.assets_path, 'reference_styles')
        
        for style_name, filename in style_files.items():
            file_path = os.path.join(reference_path, filename)
            if os.path.exists(file_path):
                try:
                    img = cv2.imread(file_path)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    styles[style_name] = img
                    logger.info(f"Loaded reference style: {style_name}")
                except Exception as e:
                    logger.warning(f"Failed to load style {style_name}: {e}")
        
        return styles
    
    async def process_image_array_async(self, 
                                       image: np.ndarray, 
                                       style: str = 'moonlight',
                                       custom_settings: Optional[Dict[str, Any]] = None,
                                       progress_callback: Optional[callable] = None) -> np.ndarray:
        """Process numpy array image with enhanced A24 style transfer"""
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        # Validate image dimensions
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected 3-channel image, got shape: {image.shape}")
        
        start_time = time.time()
        
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Ensure image is in valid range
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        try:
            if progress_callback:
                await progress_callback(5, f"Starting enhanced processing with {style} style...")
            
            # Step 1: Advanced color grading
            if progress_callback:
                await progress_callback(20, "Applying advanced color grading...")
            result = self._apply_advanced_color_grading(image, style)
            
            # Step 2: Film emulation
            if progress_callback:
                await progress_callback(40, "Adding film emulation effects...")
            result = self._apply_film_emulation(result, style)
            
            # Step 3: Lighting enhancement
            if progress_callback:
                await progress_callback(60, "Enhancing lighting and shadows...")
            result = self._enhance_lighting(result, style)
            
            # Step 4: Texture and grain
            if progress_callback:
                await progress_callback(80, "Adding film grain and texture...")
            result = self._add_film_grain_advanced(result, style)
            
            # Step 5: Final color correction
            if progress_callback:
                await progress_callback(95, "Final color correction...")
            result = self._final_color_correction(result, style, custom_settings)
            
            # Final validation
            if result is None or result.size == 0:
                logger.warning("Enhanced processing returned empty result, returning original")
                return image
            
            # Ensure result is in valid format
            result = np.clip(result, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Enhanced processing error: {e}")
            import traceback
            traceback.print_exc()
            return image
        
        processing_time = time.time() - start_time
        logger.info(f"Enhanced processing completed in {processing_time:.2f} seconds")
        
        return result
    
    def _apply_advanced_color_grading(self, image: np.ndarray, style: str) -> np.ndarray:
        """Apply advanced color grading based on A24 movie aesthetics"""
        result = image.copy().astype(np.float32) / 255.0
        
        if style == 'moonlight':
            # Cyan-magenta coastal dream with enhanced color separation
            result = self._apply_color_matrix(result, [
                [0.9, 0.1, 0.1],   # Red channel
                [0.0, 1.1, 0.2],   # Green channel  
                [0.2, 0.1, 1.2]    # Blue channel
            ])
            # Add subtle color temperature shift
            result = self._adjust_temperature(result, -300)  # Cooler
            
        elif style == 'hereditary':
            # Warm interiors with unsettling green undertones
            result = self._apply_color_matrix(result, [
                [1.2, 0.1, 0.0],   # Enhanced reds
                [0.1, 1.0, 0.1],   # Subtle green boost
                [0.0, 0.2, 0.8]    # Reduced blues
            ])
            # Add warm temperature
            result = self._adjust_temperature(result, 200)
            
        elif style == 'green_knight':
            # Medieval earthiness with candlelit warmth
            result = self._apply_color_matrix(result, [
                [1.1, 0.1, 0.0],   # Warm reds
                [0.2, 1.0, 0.1],   # Earth greens
                [0.0, 0.1, 0.7]    # Muted blues
            ])
            # Add sepia-like warmth
            result = self._add_sepia_tone(result, 0.3)
            
        elif style == 'lighthouse':
            # High contrast black and white with dramatic shadows
            # Convert to grayscale first
            gray = np.dot(result, [0.299, 0.587, 0.114])
            # Increase contrast dramatically
            gray = self._apply_contrast_curve(gray, 2.5)
            # Convert back to RGB
            result = np.stack([gray, gray, gray], axis=2)
            
        elif style == 'eighth_grade':
            # Natural digital look with subtle warmth
            result = self._apply_color_matrix(result, [
                [1.05, 0.02, 0.0],  # Slight red boost
                [0.01, 1.02, 0.01], # Slight green boost
                [0.0, 0.01, 0.98]   # Slight blue reduction
            ])
            
        elif style == 'midsommar':
            # Bright daylight horror with saturated pastels
            result = self._apply_color_matrix(result, [
                [1.3, 0.1, 0.1],   # Boosted reds
                [0.05, 1.2, 0.05], # Boosted greens
                [0.1, 0.1, 1.1]    # Boosted blues
            ])
            # Increase overall brightness
            result = np.clip(result + 0.1, 0, 1)
        
        return np.clip(result, 0, 1)
    
    def _apply_color_matrix(self, image: np.ndarray, matrix: list) -> np.ndarray:
        """Apply a 3x3 color transformation matrix"""
        matrix = np.array(matrix)
        h, w, c = image.shape
        image_flat = image.reshape(-1, c)
        result_flat = np.dot(image_flat, matrix.T)
        return result_flat.reshape(h, w, c)
    
    def _adjust_temperature(self, image: np.ndarray, kelvin_shift: int) -> np.ndarray:
        """Adjust color temperature (positive = warmer, negative = cooler)"""
        result = image.copy()
        
        if kelvin_shift > 0:  # Warmer
            factor = kelvin_shift / 1000.0
            result[:,:,0] = np.clip(result[:,:,0] + factor * 0.1, 0, 1)  # More red
            result[:,:,2] = np.clip(result[:,:,2] - factor * 0.05, 0, 1)  # Less blue
        else:  # Cooler
            factor = abs(kelvin_shift) / 1000.0
            result[:,:,0] = np.clip(result[:,:,0] - factor * 0.05, 0, 1)  # Less red
            result[:,:,2] = np.clip(result[:,:,2] + factor * 0.1, 0, 1)  # More blue
        
        return result
    
    def _add_sepia_tone(self, image: np.ndarray, strength: float) -> np.ndarray:
        """Add sepia tone effect"""
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        
        h, w, c = image.shape
        image_flat = image.reshape(-1, c)
        sepia_flat = np.dot(image_flat, sepia_matrix.T)
        sepia_image = sepia_flat.reshape(h, w, c)
        
        # Blend with original
        return image * (1 - strength) + sepia_image * strength
    
    def _apply_contrast_curve(self, image: np.ndarray, gamma: float) -> np.ndarray:
        """Apply contrast curve using gamma correction"""
        return np.power(image, gamma)
    
    def _apply_film_emulation(self, image: np.ndarray, style: str) -> np.ndarray:
        """Apply film emulation characteristics"""
        result = image.copy()
        
        # Apply film response curve
        if style in ['moonlight', 'green_knight']:
            # Soft film response
            result = self._apply_film_curve(result, 'soft')
        elif style in ['hereditary', 'lighthouse']:
            # High contrast film response
            result = self._apply_film_curve(result, 'high_contrast')
        else:
            # Digital film response
            result = self._apply_film_curve(result, 'digital')
        
        # Add subtle color bleeding
        result = self._add_color_bleeding(result, 0.1)
        
        return result
    
    def _apply_film_curve(self, image: np.ndarray, curve_type: str) -> np.ndarray:
        """Apply different film response curves"""
        if curve_type == 'soft':
            # Soft S-curve
            return 0.5 * np.sin(np.pi * (image - 0.5)) + 0.5
        elif curve_type == 'high_contrast':
            # High contrast S-curve
            return 0.5 * (np.tanh(4 * (image - 0.5)) + 1)
        else:  # digital
            # Subtle digital curve
            return np.power(image, 0.9)
    
    def _add_color_bleeding(self, image: np.ndarray, strength: float) -> np.ndarray:
        """Add subtle color bleeding between channels"""
        result = image.copy()
        
        # Slight channel mixing
        result[:,:,0] = result[:,:,0] + strength * 0.1 * result[:,:,1]  # Red gets some green
        result[:,:,1] = result[:,:,1] + strength * 0.05 * result[:,:,0]  # Green gets some red
        result[:,:,2] = result[:,:,2] + strength * 0.05 * result[:,:,1]  # Blue gets some green
        
        return np.clip(result, 0, 1)
    
    def _enhance_lighting(self, image: np.ndarray, style: str) -> np.ndarray:
        """Enhance lighting and shadow characteristics"""
        result = image.copy()
        
        # Create luminance mask
        luminance = np.dot(result, [0.299, 0.587, 0.114])
        
        # Shadow and highlight masks
        shadow_mask = np.where(luminance < 0.3, (0.3 - luminance) / 0.3, 0)
        highlight_mask = np.where(luminance > 0.7, (luminance - 0.7) / 0.3, 0)
        
        if style == 'moonlight':
            # Cool shadows, warm highlights
            shadow_color = np.array([0.8, 0.9, 1.2])  # Cool blue
            highlight_color = np.array([1.1, 1.0, 0.9])  # Warm
        elif style == 'hereditary':
            # Warm highlights, green shadows
            shadow_color = np.array([0.9, 1.1, 0.8])  # Green tint
            highlight_color = np.array([1.2, 1.1, 0.9])  # Warm orange
        elif style == 'lighthouse':
            # Dramatic contrast
            shadow_color = np.array([0.7, 0.7, 0.7])  # Darker shadows
            highlight_color = np.array([1.3, 1.3, 1.3])  # Brighter highlights
        else:
            # Neutral enhancement
            shadow_color = np.array([0.95, 0.95, 0.95])
            highlight_color = np.array([1.05, 1.05, 1.05])
        
        # Apply color tinting to shadows and highlights
        for i in range(3):
            result[:,:,i] = result[:,:,i] * (1 + shadow_mask * (shadow_color[i] - 1) * 0.2)
            result[:,:,i] = result[:,:,i] * (1 + highlight_mask * (highlight_color[i] - 1) * 0.2)
        
        return np.clip(result, 0, 1)
    
    def _add_film_grain_advanced(self, image: np.ndarray, style: str) -> np.ndarray:
        """Add advanced film grain simulation"""
        result = (image * 255).astype(np.uint8)
        h, w = result.shape[:2]
        
        # Different grain characteristics for different styles
        if style in ['lighthouse', 'hereditary']:
            # Coarse 16mm-like grain
            grain_strength = 25
            grain_size = 1.5
        elif style in ['moonlight', 'green_knight']:
            # Medium 35mm-like grain
            grain_strength = 15
            grain_size = 1.0
        else:
            # Fine digital grain
            grain_strength = 10
            grain_size = 0.8
        
        # Generate noise with different frequencies
        noise_fine = np.random.normal(0, grain_strength * 0.6, (h, w))
        noise_coarse = np.random.normal(0, grain_strength * 0.4, (h//2, w//2))
        noise_coarse = cv2.resize(noise_coarse, (w, h))
        
        # Combine noise
        total_noise = noise_fine + noise_coarse
        
        # Apply grain to each channel with slight variations
        result_float = result.astype(np.float32)
        for i in range(3):
            channel_noise = total_noise * (0.8 + 0.4 * np.random.random())
            result_float[:,:,i] += channel_noise
        
        return np.clip(result_float, 0, 255).astype(np.uint8)
    
    def _final_color_correction(self, image: np.ndarray, style: str, custom_settings: Optional[Dict] = None) -> np.ndarray:
        """Apply final color correction and custom adjustments"""
        result = image.astype(np.float32) / 255.0
        
        # Apply custom settings if provided
        if custom_settings:
            if 'brightness' in custom_settings:
                brightness = max(-0.3, min(0.3, custom_settings['brightness'] / 100.0))
                result = np.clip(result + brightness, 0, 1)
            
            if 'contrast' in custom_settings:
                contrast = max(0.5, min(2.0, custom_settings['contrast']))
                result = np.clip((result - 0.5) * contrast + 0.5, 0, 1)
            
            if 'saturation' in custom_settings:
                saturation = max(0.0, min(2.0, custom_settings['saturation']))
                hsv = cv2.cvtColor((result * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
                hsv[:,:,1] *= saturation
                hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
                result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
        
        # Style-specific final adjustments
        if style == 'moonlight':
            # Slight desaturation for dreamy look
            result = self._adjust_saturation(result, 0.85)
        elif style == 'hereditary':
            # Slight saturation boost for unsettling feel
            result = self._adjust_saturation(result, 1.1)
        elif style == 'lighthouse':
            # Ensure high contrast is maintained
            result = self._apply_contrast_curve(result, 1.2)
        
        return (result * 255).astype(np.uint8)
    
    def _adjust_saturation(self, image: np.ndarray, factor: float) -> np.ndarray:
        """Adjust saturation of the image"""
        hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:,:,1] *= factor
        hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
    
    def process_image_array(self, 
                           image: np.ndarray, 
                           style: str = 'moonlight',
                           custom_settings: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Synchronous wrapper for enhanced processing"""
        import asyncio
        
        try:
            # Run async processing in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.process_image_array_async(image, style, custom_settings)
            )
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Sync processing wrapper error: {e}")
            return image
    
    def get_available_styles(self) -> list:
        """Get list of available A24 styles"""
        return ['moonlight', 'hereditary', 'green_knight', 'lighthouse', 'eighth_grade', 'midsommar']
    
    def get_style_info(self) -> dict:
        """Get detailed information about each style"""
        return {
            'moonlight': {
                'name': 'Moonlight',
                'description': 'Dreamy cyan-magenta coastal atmosphere with soft, ethereal lighting',
                'mood': 'contemplative, intimate, ethereal',
                'characteristics': 'Cool shadows, warm highlights, desaturated colors'
            },
            'hereditary': {
                'name': 'Hereditary',
                'description': 'Warm interiors contrasted with unsettling green-tinted shadows',
                'mood': 'unsettling, warm-cold contrast, domestic horror',
                'characteristics': 'Orange highlights, green shadows, high contrast'
            },
            'green_knight': {
                'name': 'The Green Knight',
                'description': 'Medieval earthiness with candlelit warmth and natural textures',
                'mood': 'mystical, earthy, medieval',
                'characteristics': 'Sepia tones, warm candlelight, earthy greens'
            },
            'lighthouse': {
                'name': 'The Lighthouse',
                'description': 'High contrast black and white with crushing claustrophobia',
                'mood': 'claustrophobic, dramatic, maritime',
                'characteristics': 'Monochrome, extreme contrast, dramatic shadows'
            },
            'eighth_grade': {
                'name': 'Eighth Grade',
                'description': 'Natural digital look with subtle warmth and authentic feel',
                'mood': 'authentic, contemporary, coming-of-age',
                'characteristics': 'Natural colors, subtle warmth, digital clarity'
            },
            'midsommar': {
                'name': 'Midsommar',
                'description': 'Bright daylight horror with saturated pastels and Nordic clarity',
                'mood': 'bright horror, pastoral, unsettling beauty',
                'characteristics': 'Saturated pastels, bright exposure, unnatural beauty'
            }
        }
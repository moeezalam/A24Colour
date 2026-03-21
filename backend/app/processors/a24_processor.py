import cv2
import numpy as np
import os
from typing import Dict, Any, Optional
import time

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
        
        # Validate image dimensions
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError(f"Expected 3-channel image, got shape: {image.shape}")
        
        start_time = time.time()
        
        # Convert BGR to RGB if needed (OpenCV loads as BGR)
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume BGR input from OpenCV and convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Ensure image is in valid range
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Get preset settings
        settings = self.presets.get(style, self.presets['moonlight']).copy()
        if custom_settings:
            settings.update(custom_settings)
        
        # Processing pipeline with error handling
        result = image.copy()
        
        try:
            print(f"Starting processing with image shape: {result.shape}")
            
            # Step 1: Color grading
            result = self._apply_color_grading_safe(result, settings)
            print(f"After color grading: {result.shape}, dtype: {result.dtype}")
            
            # Step 2: Lighting simulation
            result = self._apply_lighting_safe(result, settings)
            print(f"After lighting: {result.shape}, dtype: {result.dtype}")
            
            # Step 3: Film texture
            result = self._apply_film_texture_safe(result, settings)
            print(f"After film texture: {result.shape}, dtype: {result.dtype}")
            
            # Step 4: Composition and aspect ratio
            result = self._apply_composition_safe(result, settings)
            print(f"After composition: {result.shape}, dtype: {result.dtype}")
            
            # Final validation
            if result is None or result.size == 0:
                print("Warning: Result is empty, returning original")
                return image
            
            # Ensure result is in valid format
            result = np.clip(result, 0, 255).astype(np.uint8)
            
        except Exception as e:
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
            # Return original image if processing fails
            return image
        
        processing_time = time.time() - start_time
        print(f"Processing completed in {processing_time:.2f} seconds")
        
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
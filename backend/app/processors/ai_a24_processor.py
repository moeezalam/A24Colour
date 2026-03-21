import cv2
import numpy as np
import os
from typing import Dict, Any, Optional
import time
import logging

from ..services.style_transfer_service import A24StyleTransferService

logger = logging.getLogger(__name__)

class AIA24StyleProcessor:
    """AI-powered A24 style processor using TensorFlow Hub"""
    
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self.style_service = A24StyleTransferService(assets_path)
        logger.info("AI A24 Style Processor initialized")
    
    async def process_image_array_async(self, 
                                       image: np.ndarray, 
                                       style: str = 'moonlight',
                                       custom_settings: Optional[Dict[str, Any]] = None,
                                       progress_callback: Optional[callable] = None) -> np.ndarray:
        """Process numpy array image with AI A24 style transfer"""
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
        
        try:
            if progress_callback:
                await progress_callback(5, f"Starting AI processing with {style} style...")
            
            # Use AI style transfer service
            result = await self.style_service.transfer_style_async(
                content_image=image,
                style_name=style,
                custom_settings=custom_settings,
                progress_callback=progress_callback
            )
            
            # Final validation
            if result is None or result.size == 0:
                logger.warning("AI processing returned empty result, returning original")
                return image
            
            # Ensure result is in valid format
            result = np.clip(result, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            import traceback
            traceback.print_exc()
            # Return original image if AI processing fails
            return image
        
        processing_time = time.time() - start_time
        logger.info(f"AI processing completed in {processing_time:.2f} seconds")
        
        return result
    
    def process_image_array(self, 
                           image: np.ndarray, 
                           style: str = 'moonlight',
                           custom_settings: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """Synchronous wrapper for AI processing"""
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
        return self.style_service.get_available_styles()
    
    def get_style_info(self) -> dict:
        """Get detailed information about each style"""
        return self.style_service.get_style_info()
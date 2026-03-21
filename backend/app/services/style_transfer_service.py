import numpy as np
import cv2
from typing import Optional, Tuple
import os
import logging
from PIL import Image
import asyncio
import concurrent.futures

# Try to import TensorFlow, but gracefully handle if it fails
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    TF_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("TensorFlow and TensorFlow Hub loaded successfully")
except ImportError as e:
    TF_AVAILABLE = False
    tf = None
    hub = None
    logger = logging.getLogger(__name__)
    logger.warning(f"TensorFlow not available: {e}. Using fallback processing.")

class A24StyleTransferService:
    """AI-powered A24 style transfer using TensorFlow Hub"""
    
    def __init__(self, assets_path: str):
        self.assets_path = assets_path
        self.model = None
        self.reference_styles = {}
        self._initialize_model()
        self._load_reference_styles()
    
    def _initialize_model(self):
        """Initialize TensorFlow Hub style transfer model"""
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available, using fallback processing")
            self.model = None
            return
            
        try:
            logger.info("Loading TensorFlow Hub style transfer model...")
            # Set environment for optimized model loading
            os.environ['TFHUB_MODEL_LOAD_FORMAT'] = 'COMPRESSED'
            
            # Load the pre-trained model
            model_url = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
            self.model = hub.load(model_url)
            
            logger.info("Style transfer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load style transfer model: {e}")
            # Fallback to a simpler approach if TensorFlow Hub fails
            self.model = None
            logger.warning("Using fallback processing instead of AI model")
    
    def _load_reference_styles(self):
        """Load A24 movie reference style images"""
        style_files = {
            'moonlight': 'moonlight_reference.jpg',
            'hereditary': 'hereditary_reference.jpg',
            'green_knight': 'green_knight_reference.jpg',
            'lighthouse': 'lighthouse_reference.jpg',
            'eighth_grade': 'eighth_grade_reference.jpg',
            'midsommar': 'midsommar_reference.jpg'
        }
        
        reference_path = os.path.join(self.assets_path, 'reference_styles')
        
        # Create reference styles directory if it doesn't exist
        os.makedirs(reference_path, exist_ok=True)
        
        for style_name, filename in style_files.items():
            file_path = os.path.join(reference_path, filename)
            
            if os.path.exists(file_path):
                try:
                    # Load and preprocess style image
                    style_image = self._load_and_preprocess_image(file_path)
                    self.reference_styles[style_name] = style_image
                    logger.info(f"Loaded reference style: {style_name}")
                except Exception as e:
                    logger.warning(f"Failed to load style {style_name}: {e}")
                    # Create a synthetic reference style
                    self.reference_styles[style_name] = self._create_synthetic_style(style_name)
            else:
                logger.warning(f"Reference style not found: {file_path}")
                # Create a synthetic reference style
                self.reference_styles[style_name] = self._create_synthetic_style(style_name)
    
    def _create_synthetic_style(self, style_name: str):
        """Create synthetic reference style if file doesn't exist"""
        # Create a 256x256 synthetic style image
        height, width = 256, 256
        
        if style_name == 'moonlight':
            # Cyan-magenta gradient
            image = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    # Radial gradient
                    center_x, center_y = width // 2, height // 2
                    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    max_distance = np.sqrt(center_x**2 + center_y**2)
                    norm_distance = distance / max_distance
                    
                    cyan_factor = 1 - norm_distance
                    magenta_factor = norm_distance
                    
                    image[y, x] = [
                        int(cyan_factor * 255 + magenta_factor * 200),  # R
                        int(cyan_factor * 200 + magenta_factor * 100),  # G  
                        int(cyan_factor * 255 + magenta_factor * 255)   # B
                    ]
        
        elif style_name == 'hereditary':
            # Warm orange with green undertones
            image = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    warm_factor = y / height
                    image[y, x] = [
                        int((1 - warm_factor) * 255 + warm_factor * 80),   # R
                        int((1 - warm_factor) * 220 + warm_factor * 120),  # G
                        int((1 - warm_factor) * 180 + warm_factor * 100)   # B
                    ]
        
        elif style_name == 'lighthouse':
            # High contrast black and white
            image = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    # Checkerboard-like pattern for high contrast
                    if (x // 32 + y // 32) % 2:
                        image[y, x] = [240, 240, 240]  # Light gray
                    else:
                        image[y, x] = [40, 40, 40]     # Dark gray
        
        else:
            # Default gradient for other styles
            image = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    image[y, x] = [
                        int(255 * x / width),
                        int(255 * y / height),
                        128
                    ]
        
        # Convert to tensor if TensorFlow is available
        if TF_AVAILABLE:
            img_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
            img_tensor = img_tensor / 255.0
            img_tensor = img_tensor[tf.newaxis, :]  # Add batch dimension
            return img_tensor
        else:
            # Return numpy array for fallback processing
            return image.astype(np.float32) / 255.0
    
    def _load_and_preprocess_image(self, image_path: str, max_dim: int = 512):
        """Load and preprocess image for style transfer"""
        if TF_AVAILABLE:
            # Read image file
            img = tf.io.read_file(image_path)
            img = tf.image.decode_image(img, channels=3)
            img = tf.image.convert_image_dtype(img, tf.float32)
            
            # Resize while maintaining aspect ratio
            shape = tf.cast(tf.shape(img)[:-1], tf.float32)
            long_dim = max(shape)
            scale = max_dim / long_dim
            new_shape = tf.cast(shape * scale, tf.int32)
            
            img = tf.image.resize(img, new_shape)
            img = img[tf.newaxis, :]  # Add batch dimension
            
            return img
        else:
            # Fallback using OpenCV
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize while maintaining aspect ratio
            h, w = img.shape[:2]
            long_dim = max(h, w)
            scale = max_dim / long_dim
            new_h, new_w = int(h * scale), int(w * scale)
            
            img = cv2.resize(img, (new_w, new_h))
            img = img.astype(np.float32) / 255.0
            
            return img
    
    def _preprocess_content_image(self, image_array: np.ndarray, max_dim: int = 512):
        """Preprocess uploaded content image"""
        if TF_AVAILABLE:
            # Convert numpy array to tensor
            img = tf.convert_to_tensor(image_array, dtype=tf.float32)
            img = img / 255.0  # Normalize to [0,1]
            
            # Resize while maintaining aspect ratio
            shape = tf.cast(tf.shape(img)[:-1], tf.float32)
            long_dim = max(shape)
            scale = max_dim / long_dim
            new_shape = tf.cast(shape * scale, tf.int32)
            
            img = tf.image.resize(img, new_shape)
            img = img[tf.newaxis, :]  # Add batch dimension
            
            return img
        else:
            # Fallback using OpenCV
            img = image_array.astype(np.float32) / 255.0
            
            # Resize while maintaining aspect ratio
            h, w = img.shape[:2]
            long_dim = max(h, w)
            if long_dim > max_dim:
                scale = max_dim / long_dim
                new_h, new_w = int(h * scale), int(w * scale)
                img = cv2.resize(img, (new_w, new_h))
            
            return img
    
    async def transfer_style_async(self, 
                                  content_image: np.ndarray,
                                  style_name: str,
                                  custom_settings: Optional[dict] = None,
                                  progress_callback: Optional[callable] = None) -> np.ndarray:
        """Asynchronously transfer style to content image"""
        
        if progress_callback:
            await progress_callback(0, "Initializing style transfer...")
        
        # Validate style
        if style_name not in self.reference_styles:
            available_styles = list(self.reference_styles.keys())
            raise ValueError(f"Style '{style_name}' not available. Available styles: {available_styles}")
        
        if progress_callback:
            await progress_callback(20, "Preprocessing images...")
        
        # Preprocess images
        content_tensor = self._preprocess_content_image(content_image)
        style_tensor = self.reference_styles[style_name]
        
        if progress_callback:
            await progress_callback(40, "Applying AI style transfer...")
        
        # Run style transfer
        if self.model is not None:
            # Use AI model
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                stylized_tensor = await loop.run_in_executor(
                    executor,
                    self._run_style_transfer,
                    content_tensor,
                    style_tensor
                )
        else:
            # Fallback to simple processing
            stylized_tensor = self._fallback_processing(content_tensor, style_name)
        
        if progress_callback:
            await progress_callback(80, "Post-processing result...")
        
        # Convert back to numpy array
        stylized_image = self._tensor_to_numpy(stylized_tensor)
        
        # Apply custom adjustments if provided
        if custom_settings:
            stylized_image = self._apply_custom_adjustments(stylized_image, custom_settings)
        
        if progress_callback:
            await progress_callback(100, "Style transfer complete!")
        
        return stylized_image
    
    def _run_style_transfer(self, content_tensor, style_tensor):
        """Run the actual style transfer model"""
        try:
            # Run the model
            stylized_tensor = self.model(content_tensor, style_tensor)[0]
            return stylized_tensor
        except Exception as e:
            logger.error(f"Style transfer model execution failed: {e}")
            # Fallback to simple blending
            return content_tensor
    
    def _fallback_processing(self, content_tensor, style_name: str):
        """Fallback processing when AI model is not available"""
        # Simple color adjustments based on style
        if TF_AVAILABLE and hasattr(content_tensor, 'numpy'):
            content_array = content_tensor.numpy()
            if len(content_array.shape) == 4:  # Has batch dimension
                content_array = content_array[0]  # Remove batch dimension
        else:
            content_array = content_tensor
        
        if style_name == 'moonlight':
            # Apply cyan-magenta tint
            content_array[:,:,0] = np.clip(content_array[:,:,0] * 0.9 + 0.1, 0, 1)  # R
            content_array[:,:,1] = np.clip(content_array[:,:,1] * 1.1, 0, 1)        # G
            content_array[:,:,2] = np.clip(content_array[:,:,2] * 1.2, 0, 1)        # B
        
        elif style_name == 'hereditary':
            # Apply warm-green tint
            content_array[:,:,0] = np.clip(content_array[:,:,0] * 1.2, 0, 1)        # R
            content_array[:,:,1] = np.clip(content_array[:,:,1] * 1.0, 0, 1)        # G
            content_array[:,:,2] = np.clip(content_array[:,:,2] * 0.8, 0, 1)        # B
        
        elif style_name == 'lighthouse':
            # Convert to high contrast grayscale
            gray = np.dot(content_array, [0.299, 0.587, 0.114])
            # Increase contrast
            gray = np.clip((gray - 0.5) * 2 + 0.5, 0, 1)
            content_array[:,:,0] = gray
            content_array[:,:,1] = gray
            content_array[:,:,2] = gray
        
        elif style_name == 'green_knight':
            # Apply earthy medieval tones
            content_array[:,:,0] = np.clip(content_array[:,:,0] * 1.1 + 0.05, 0, 1)  # R
            content_array[:,:,1] = np.clip(content_array[:,:,1] * 1.0 + 0.1, 0, 1)   # G
            content_array[:,:,2] = np.clip(content_array[:,:,2] * 0.7, 0, 1)         # B
        
        elif style_name == 'eighth_grade':
            # Apply subtle warm digital look
            content_array[:,:,0] = np.clip(content_array[:,:,0] * 1.05, 0, 1)        # R
            content_array[:,:,1] = np.clip(content_array[:,:,1] * 1.02, 0, 1)        # G
            content_array[:,:,2] = np.clip(content_array[:,:,2] * 0.98, 0, 1)        # B
        
        elif style_name == 'midsommar':
            # Apply bright pastel look
            content_array[:,:,0] = np.clip(content_array[:,:,0] * 1.3 + 0.1, 0, 1)   # R
            content_array[:,:,1] = np.clip(content_array[:,:,1] * 1.2 + 0.05, 0, 1)  # G
            content_array[:,:,2] = np.clip(content_array[:,:,2] * 1.1, 0, 1)         # B
        
        # Clip values and return
        content_array = np.clip(content_array, 0, 1)
        
        if TF_AVAILABLE:
            return tf.convert_to_tensor(content_array[np.newaxis, :], dtype=tf.float32)
        else:
            return content_array
    
    def _tensor_to_numpy(self, tensor) -> np.ndarray:
        """Convert TensorFlow tensor to numpy array"""
        if TF_AVAILABLE and hasattr(tensor, 'numpy'):
            # Remove batch dimension and convert to numpy
            if len(tensor.shape) == 4:  # Has batch dimension
                tensor = tf.squeeze(tensor, axis=0)
            array = tensor.numpy()
        else:
            # Already a numpy array
            array = tensor
        
        # Convert to 0-255 range and uint8
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)
        
        return array
    
    def _apply_custom_adjustments(self, image: np.ndarray, settings: dict) -> np.ndarray:
        """Apply custom post-processing adjustments"""
        result = image.copy()
        
        # Brightness adjustment
        if 'brightness' in settings:
            brightness = max(-100, min(100, settings['brightness']))
            result = cv2.convertScaleAbs(result, alpha=1.0, beta=brightness)
        
        # Contrast adjustment
        if 'contrast' in settings:
            contrast = max(0.5, min(2.0, settings['contrast']))
            result = cv2.convertScaleAbs(result, alpha=contrast, beta=0)
        
        # Saturation adjustment
        if 'saturation' in settings:
            saturation = max(0.0, min(2.0, settings['saturation']))
            hsv = cv2.cvtColor(result, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] *= saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        
        return result
    
    def get_available_styles(self) -> list:
        """Get list of available A24 styles"""
        return list(self.reference_styles.keys())
    
    def get_style_info(self) -> dict:
        """Get detailed information about each style"""
        return {
            'moonlight': {
                'name': 'Moonlight',
                'description': 'Dreamy cyan-magenta coastal atmosphere with soft, ethereal lighting',
                'mood': 'contemplative, intimate, ethereal'
            },
            'hereditary': {
                'name': 'Hereditary',
                'description': 'Warm interiors contrasted with unsettling green-tinted shadows',
                'mood': 'unsettling, warm-cold contrast, domestic horror'
            },
            'green_knight': {
                'name': 'The Green Knight',
                'description': 'Medieval earthiness with candlelit warmth and natural textures',
                'mood': 'mystical, earthy, medieval'
            },
            'lighthouse': {
                'name': 'The Lighthouse',
                'description': 'High contrast black and white with crushing claustrophobia',
                'mood': 'claustrophobic, dramatic, maritime'
            },
            'eighth_grade': {
                'name': 'Eighth Grade',
                'description': 'Natural digital look with subtle warmth and authentic feel',
                'mood': 'authentic, contemporary, coming-of-age'
            },
            'midsommar': {
                'name': 'Midsommar',
                'description': 'Bright daylight horror with saturated pastels and Nordic clarity',
                'mood': 'bright horror, pastoral, unsettling beauty'
            }
        }
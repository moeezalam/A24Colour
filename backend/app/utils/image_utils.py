import cv2
import numpy as np
from PIL import Image
from fastapi import UploadFile
from fastapi.responses import Response
import io
import base64

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

def numpy_to_base64(image: np.ndarray, format: str = 'JPEG') -> str:
    """Convert numpy array to base64 string"""
    # Convert RGB to BGR for OpenCV
    if len(image.shape) == 3 and image.shape[2] == 3:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image_bgr = image
    
    # Encode image
    if format.upper() == 'JPEG':
        _, buffer = cv2.imencode('.jpg', image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    else:
        _, buffer = cv2.imencode('.png', image_bgr)
    
    # Convert to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/{format.lower()};base64,{img_base64}"
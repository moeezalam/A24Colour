#!/usr/bin/env python3
"""
Simple test script to debug image processing issues
"""

import cv2
import numpy as np
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.processors.a24_processor import A24StyleProcessor

def create_test_image():
    """Create a simple test image"""
    # Create a 400x300 RGB test image with gradient
    height, width = 300, 400
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a gradient
    for y in range(height):
        for x in range(width):
            image[y, x, 0] = int(255 * x / width)  # Red gradient
            image[y, x, 1] = int(255 * y / height)  # Green gradient
            image[y, x, 2] = 128  # Constant blue
    
    return image

def test_processing():
    """Test the A24 processing pipeline"""
    print("Creating test image...")
    test_image = create_test_image()
    print(f"Test image shape: {test_image.shape}, dtype: {test_image.dtype}")
    
    # Save original
    cv2.imwrite('test_original.jpg', cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR))
    print("Saved test_original.jpg")
    
    # Initialize processor
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
    processor = A24StyleProcessor(assets_path)
    
    # Test each style
    styles = ['moonlight', 'hereditary', 'lighthouse']
    
    for style in styles:
        print(f"\nTesting {style} style...")
        try:
            # Process image
            result = processor.process_image_array(test_image, style)
            print(f"Result shape: {result.shape}, dtype: {result.dtype}")
            
            # Check for black regions
            black_pixels = np.sum(np.all(result == 0, axis=2))
            total_pixels = result.shape[0] * result.shape[1]
            black_percentage = (black_pixels / total_pixels) * 100
            print(f"Black pixels: {black_pixels}/{total_pixels} ({black_percentage:.2f}%)")
            
            # Save result
            filename = f'test_{style}.jpg'
            cv2.imwrite(filename, cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
            print(f"Saved {filename}")
            
        except Exception as e:
            print(f"Error processing {style}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_processing()
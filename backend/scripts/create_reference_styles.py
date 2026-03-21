#!/usr/bin/env python3
"""
Create reference style images for A24 movies
"""

import cv2
import numpy as np
import os
from pathlib import Path

def create_style_reference(style_name: str, style_info: dict) -> np.ndarray:
    """Create a synthetic reference image with A24 characteristics"""
    
    # Create base image (512x512)
    height, width = 512, 512
    reference = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Generate color gradient based on style
    if style_name == 'moonlight':
        # Cyan-magenta gradient with soft lighting
        for y in range(height):
            for x in range(width):
                # Radial gradient from center
                center_x, center_y = width // 2, height // 2
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_distance = np.sqrt(center_x**2 + center_y**2)
                norm_distance = distance / max_distance
                
                # Cyan to magenta gradient
                cyan_factor = 1 - norm_distance
                magenta_factor = norm_distance
                
                reference[y, x] = [
                    int(cyan_factor * 100 + magenta_factor * 200),  # B
                    int(cyan_factor * 200 + magenta_factor * 100),  # G  
                    int(cyan_factor * 255 + magenta_factor * 200)   # R
                ]
    
    elif style_name == 'hereditary':
        # Warm orange interior with green shadows
        for y in range(height):
            for x in range(width):
                # Vertical gradient (warm top, green bottom)
                warm_factor = y / height
                
                reference[y, x] = [
                    int((1 - warm_factor) * 180 + warm_factor * 100),  # B
                    int((1 - warm_factor) * 220 + warm_factor * 120),  # G
                    int((1 - warm_factor) * 255 + warm_factor * 80)    # R
                ]
    
    elif style_name == 'green_knight':
        # Earth tones with candlelight warmth
        for y in range(height):
            for x in range(width):
                # Diagonal gradient
                diag_factor = (x + y) / (width + height)
                
                reference[y, x] = [
                    int((1 - diag_factor) * 40 + diag_factor * 120),   # B
                    int((1 - diag_factor) * 80 + diag_factor * 180),   # G
                    int((1 - diag_factor) * 60 + diag_factor * 200)    # R
                ]
    
    elif style_name == 'lighthouse':
        # High contrast black and white
        for y in range(height):
            for x in range(width):
                # Checkerboard-like pattern for high contrast
                if (x // 64 + y // 64) % 2:
                    reference[y, x] = [240, 240, 240]  # Light gray
                else:
                    reference[y, x] = [20, 20, 20]     # Dark gray
    
    elif style_name == 'eighth_grade':
        # Natural digital look with subtle warmth
        for y in range(height):
            for x in range(width):
                # Subtle warm gradient
                warm_factor = 0.3 + 0.4 * (x / width)
                
                reference[y, x] = [
                    int(200 + warm_factor * 55),   # B
                    int(210 + warm_factor * 45),   # G
                    int(220 + warm_factor * 35)    # R
                ]
    
    elif style_name == 'midsommar':
        # Bright pastels with saturated colors
        for y in range(height):
            for x in range(width):
                # Bright pastel gradient
                pastel_factor = 0.7 + 0.3 * np.sin(x / width * np.pi)
                
                reference[y, x] = [
                    int(150 + pastel_factor * 105),  # B
                    int(200 + pastel_factor * 55),   # G
                    int(255)                         # R
                ]
    
    else:
        # Default gradient
        for y in range(height):
            for x in range(width):
                reference[y, x] = [
                    int(255 * x / width),
                    int(255 * y / height),
                    128
                ]
    
    # Add film grain texture
    grain = np.random.normal(0, 10, (height, width, 3)).astype(np.int16)
    reference = np.clip(reference.astype(np.int16) + grain, 0, 255).astype(np.uint8)
    
    # Apply Gaussian blur for softness
    reference = cv2.GaussianBlur(reference, (3, 3), 1)
    
    return reference

def create_all_reference_styles():
    """Create reference style images for all A24 movies"""
    
    # Define movie styles
    movie_styles = {
        'moonlight': {
            'description': 'Cyan-magenta coastal dream',
        },
        'hereditary': {
            'description': 'Warm interiors, green undertones',
        },
        'green_knight': {
            'description': 'Medieval earthiness, candlelit',
        },
        'lighthouse': {
            'description': 'High contrast black and white',
        },
        'eighth_grade': {
            'description': 'Natural digital warmth',
        },
        'midsommar': {
            'description': 'Bright daylight horror pastels',
        }
    }
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "assets" / "reference_styles"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎬 Creating A24 reference style images...")
    
    # Create reference images
    for style_name, style_info in movie_styles.items():
        print(f"Creating {style_name}...")
        
        reference_image = create_style_reference(style_name, style_info)
        
        # Save reference image
        output_path = output_dir / f"{style_name}_reference.jpg"
        cv2.imwrite(str(output_path), reference_image)
        
        print(f"✅ Created reference for {style_name}: {style_info['description']}")
    
    print(f"\n🎉 All reference styles created in: {output_dir}")
    print("\nReference styles:")
    for style_name, style_info in movie_styles.items():
        print(f"  • {style_name}: {style_info['description']}")

if __name__ == "__main__":
    create_all_reference_styles()
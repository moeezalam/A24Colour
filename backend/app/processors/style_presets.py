from typing import Dict, Any

class A24StylePresets:
    """Predefined style configurations for different A24 films"""
    
    @staticmethod
    def get_all_presets() -> Dict[str, Dict[str, Any]]:
        return {
            'moonlight': {
                'name': 'Moonlight',
                'description': 'Cyan-magenta contrasts with dreamy coastal atmosphere',
                'lut': 'moonlight',
                'split_tone_highlights': (255, 200, 180),
                'split_tone_shadows': (100, 150, 200),
                'desaturation': 0.2,
                'shadow_lift': 0.15,
                'grain_type': '35mm',
                'grain_intensity': 0.25,
                'halation_strength': 0.4,
                'chromatic_aberration': 1.0,
                'aspect_ratio': 'cinematic',
                'lighting_direction': 'left',
                'lighting_intensity': 0.6,
                'temperature': 'cool'
            },
            'hereditary': {
                'name': 'Hereditary',
                'description': 'Warm interiors with unsettling green shadows',
                'lut': 'hereditary',
                'split_tone_highlights': (255, 220, 180),
                'split_tone_shadows': (80, 120, 100),
                'desaturation': 0.3,
                'shadow_lift': 0.1,
                'grain_type': '16mm',
                'grain_intensity': 0.4,
                'halation_strength': 0.2,
                'chromatic_aberration': 2.0,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top',
                'lighting_intensity': 0.7,
                'temperature': 'warm'
            },
            'green_knight': {
                'name': 'The Green Knight',
                'description': 'Medieval earthiness with candlelit warmth',
                'lut': 'green_knight',
                'split_tone_highlights': (200, 180, 120),
                'split_tone_shadows': (60, 80, 40),
                'desaturation': 0.4,
                'shadow_lift': 0.05,
                'grain_type': '35mm',
                'grain_intensity': 0.3,
                'halation_strength': 0.5,
                'chromatic_aberration': 1.5,
                'aspect_ratio': 'cinematic',
                'lighting_direction': 'right',
                'lighting_intensity': 0.5,
                'temperature': 'warm'
            },
            'lighthouse': {
                'name': 'The Lighthouse',
                'description': 'Black and white with crushing claustrophobia',
                'lut': 'lighthouse',
                'split_tone_highlights': (240, 240, 220),
                'split_tone_shadows': (40, 60, 80),
                'desaturation': 0.5,
                'shadow_lift': 0.2,
                'grain_type': '16mm',
                'grain_intensity': 0.5,
                'halation_strength': 0.3,
                'chromatic_aberration': 3.0,
                'aspect_ratio': 'academy',
                'lighting_direction': 'left',
                'lighting_intensity': 0.8,
                'temperature': 'cool'
            },
            'eighth_grade': {
                'name': 'Eighth Grade',
                'description': 'Natural digital look with subtle warmth',
                'lut': None,
                'split_tone_highlights': (255, 240, 220),
                'split_tone_shadows': (200, 210, 220),
                'desaturation': 0.1,
                'shadow_lift': 0.12,
                'grain_type': 'digital',
                'grain_intensity': 0.15,
                'halation_strength': 0.1,
                'chromatic_aberration': 0.5,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top',
                'lighting_intensity': 0.4,
                'temperature': 'neutral'
            },
            'midsommar': {
                'name': 'Midsommar',
                'description': 'Bright daylight horror with saturated pastels',
                'lut': None,
                'split_tone_highlights': (255, 250, 200),
                'split_tone_shadows': (180, 200, 150),
                'desaturation': -0.1,  # Actually increase saturation slightly
                'shadow_lift': 0.3,
                'grain_type': '35mm',
                'grain_intensity': 0.2,
                'halation_strength': 0.6,
                'chromatic_aberration': 1.0,
                'aspect_ratio': 'standard',
                'lighting_direction': 'top',
                'lighting_intensity': 0.3,
                'temperature': 'warm'
            }
        }
    
    @staticmethod
    def get_preset(name: str) -> Dict[str, Any]:
        presets = A24StylePresets.get_all_presets()
        return presets.get(name, presets['moonlight'])
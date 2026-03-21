from pydantic import BaseModel, Field
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum

class AspectRatio(str, Enum):
    ACADEMY = "academy"
    STANDARD = "standard" 
    CINEMATIC = "cinematic"
    SQUARE = "square"
    PORTRAIT = "portrait"

class GrainType(str, Enum):
    GRAIN_16MM = "16mm"
    GRAIN_35MM = "35mm"
    DIGITAL = "digital"

class LightingDirection(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

class Temperature(str, Enum):
    COOL = "cool"
    NEUTRAL = "neutral"
    WARM = "warm"

class StylePresetSchema(BaseModel):
    name: str
    description: str
    lut: Optional[str] = None
    split_tone_highlights: Tuple[int, int, int] = (255, 255, 255)
    split_tone_shadows: Tuple[int, int, int] = (0, 0, 0)
    desaturation: float = Field(default=0.3, ge=0.0, le=1.0)
    shadow_lift: float = Field(default=0.1, ge=0.0, le=0.5)
    grain_type: GrainType = GrainType.GRAIN_35MM
    grain_intensity: float = Field(default=0.3, ge=0.0, le=1.0)
    halation_strength: float = Field(default=0.3, ge=0.0, le=1.0)
    chromatic_aberration: float = Field(default=1.5, ge=0.0, le=5.0)
    aspect_ratio: AspectRatio = AspectRatio.CINEMATIC
    lighting_direction: LightingDirection = LightingDirection.LEFT
    lighting_intensity: float = Field(default=0.6, ge=0.0, le=1.0)
    temperature: Temperature = Temperature.NEUTRAL

class ProcessingRequest(BaseModel):
    style: str
    custom_settings: Optional[Dict[str, Any]] = None

class ProcessingResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None

class StylesResponse(BaseModel):
    styles: List[str]
    presets: Dict[str, StylePresetSchema]

class HealthResponse(BaseModel):
    status: str
    processor: str
    version: str
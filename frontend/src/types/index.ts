export interface StylePreset {
  name: string;
  description: string;
  lut?: string;
  split_tone_highlights: [number, number, number];
  split_tone_shadows: [number, number, number];
  desaturation: number;
  shadow_lift: number;
  grain_type: string;
  grain_intensity: number;
  halation_strength: number;
  chromatic_aberration: number;
  aspect_ratio: string;
  lighting_direction: string;
  lighting_intensity: number;
  temperature: string;
}

export interface ProcessingRequest {
  style: string;
  customSettings?: Partial<StylePreset>;
}

export interface ProcessingResponse {
  success: boolean;
  message?: string;
  processed_image?: string;
  error?: string;
}

export interface StyleOption {
  id: string;
  name: string;
  description: string;
  color: string;
}
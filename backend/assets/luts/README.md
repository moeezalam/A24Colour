# LUT Files

This directory should contain the actual LUT (.cube) files for each A24 movie style:

- `moonlight.cube` - Cyan-magenta coastal atmosphere
- `hereditary.cube` - Warm interiors with unsettling green shadows  
- `green_knight.cube` - Medieval earthiness with candlelit warmth
- `lighthouse.cube` - Black and white claustrophobic atmosphere

## Note

The current implementation uses procedural LUTs as placeholders. For production use, you would need to:

1. Obtain actual LUT files from professional colorists
2. Create custom LUTs by analyzing A24 movie frames
3. Use tools like DaVinci Resolve to generate .cube files

## LUT Format

LUT files should be in the standard .cube format with 32x32x32 or 64x64x64 resolution.
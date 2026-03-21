# A24 Style Transfer App

Transform your photos with cinematic A24 aesthetics using advanced image processing techniques.

## Features

- **6 A24 Movie Styles**: Moonlight, Hereditary, The Green Knight, The Lighthouse, Eighth Grade, Midsommar
- **Advanced Color Grading**: LUT application, split toning, desaturation
- **Film Texture Effects**: Grain, halation, chromatic aberration
- **Lighting Simulation**: Directional lighting, shadow enhancement
- **Aspect Ratio Control**: Academy, Standard, Cinematic, Square formats
- **Real-time Preview**: Before/after comparison
- **Custom Settings**: Fine-tune all parameters

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenCV** - Image processing
- **NumPy** - Mathematical operations
- **Pillow** - Image manipulation
- **Pydantic** - Data validation

### Frontend
- **React** + **TypeScript** - Modern UI framework
- **Tailwind CSS** - Utility-first styling
- **React Dropzone** - File upload handling
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd a24-style-app

# Start with Docker Compose
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Usage

1. **Upload Image**: Drag & drop or click to select an image (JPG, PNG, BMP, TIFF)
2. **Choose Style**: Select from 6 A24 movie styles
3. **Adjust Settings**: Fine-tune desaturation, grain, shadows, aspect ratio
4. **Process**: Click "Apply A24 Style" and wait for processing
5. **Download**: Save your transformed image

## API Endpoints

- `GET /` - API status
- `GET /api/v1/styles/` - List available styles
- `GET /api/v1/styles/{style_name}/` - Get style preset details
- `POST /api/v1/process-image/` - Process image with style
- `GET /api/v1/health/` - Health check

## Project Structure

```
a24-style-app/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Image processing modules
│   │   ├── models/        # Pydantic schemas
│   │   ├── processors/    # A24 style processors
│   │   └── utils/         # Utility functions
│   ├── assets/            # LUTs, textures, models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── package.json
└── docker-compose.yml
```

## Development

### Adding New Styles

1. Add style preset in `backend/app/processors/style_presets.py`
2. Add LUT file in `backend/assets/luts/`
3. Update frontend style selector in `frontend/src/components/StyleSelector.tsx`

### Customizing Processing

- **Color Grading**: Modify `backend/app/core/color_grading.py`
- **Film Texture**: Edit `backend/app/core/film_texture.py`
- **Lighting**: Update `backend/app/core/lighting_simulation.py`
- **Composition**: Change `backend/app/core/aspect_ratio.py`

## Performance

- Images are automatically resized to max 2048px
- Processing typically takes 2-5 seconds per image
- Memory usage scales with image size
- GPU acceleration available for AI models (optional)

## Limitations

- Maximum file size: 10MB
- Supported formats: JPG, PNG, BMP, TIFF
- Processing is CPU-bound (no GPU acceleration yet)
- LUT files are procedural (not actual A24 LUTs)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. A24 is a trademark of A24 Films LLC.

## Acknowledgments

- A24 Films for their distinctive visual style
- OpenCV community for image processing tools
- React and FastAPI communities for excellent frameworks
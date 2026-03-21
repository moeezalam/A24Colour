# A24 Style Transfer App - Dependencies

## System Requirements

### Required Software
- **Python 3.9+** - Main backend language
- **Node.js 16+** - Frontend development
- **npm 8+** - Package manager (comes with Node.js)
- **Git** - Version control

### Optional Software
- **Docker** - For containerized deployment
- **Docker Compose** - For multi-container orchestration

## Backend Dependencies (Python)

### Core Framework
```bash
pip install fastapi==0.104.1          # Web framework
pip install uvicorn==0.24.0           # ASGI server
```

### Image Processing
```bash
pip install opencv-python==4.8.1.78   # Computer vision library
pip install numpy==1.24.3             # Numerical computing
pip install Pillow==10.0.1            # Image manipulation
pip install scikit-image==0.21.0      # Advanced image processing
```

### API & Data Handling
```bash
pip install python-multipart==0.0.6   # File upload support
pip install pydantic==2.5.0           # Data validation
pip install aiofiles==23.2.1          # Async file operations
```

### Optional (Future Features)
```bash
pip install redis==5.0.1              # Caching/task queue
pip install celery==5.3.4             # Background tasks
pip install python-dotenv==1.0.0      # Environment variables
```

### Development Tools
```bash
pip install pytest==7.4.3             # Testing framework
pip install black==23.10.1            # Code formatter
pip install flake8==6.1.0             # Linting
```

## Frontend Dependencies (Node.js)

### Core Framework
```bash
npm install react@18.2.0              # UI library
npm install react-dom@18.2.0          # React DOM renderer
npm install typescript@4.7.4          # Type safety
```

### UI Components & Styling
```bash
npm install tailwindcss@3.3.5         # Utility-first CSS
npm install lucide-react@0.294.0      # Icon library
npm install react-dropzone@14.2.3     # File upload component
```

### HTTP & State Management
```bash
npm install axios@1.6.0               # HTTP client
```

### Development Tools
```bash
npm install react-scripts@5.0.1       # Build tools
npm install @types/react@18.0.17      # React TypeScript types
npm install @types/react-dom@18.0.6   # React DOM TypeScript types
npm install @types/node@16.11.56      # Node.js TypeScript types
npm install autoprefixer@10.4.16      # CSS post-processor
npm install postcss@8.4.31            # CSS transformer
```

### Testing
```bash
npm install @testing-library/react@13.3.0      # React testing utilities
npm install @testing-library/jest-dom@5.16.4   # Jest DOM matchers
npm install @testing-library/user-event@13.5.0 # User interaction testing
```

## Installation Commands

### Automatic Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### Docker Setup
```bash
docker-compose up --build
```

## Development Commands

### Backend Development
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

### Production Build
```bash
# Frontend
cd frontend
npm run build

# Docker
docker-compose -f docker-compose.prod.yml up --build
```

## System Dependencies

### Windows
- **Visual Studio Build Tools** (for some Python packages)
- **Windows Subsystem for Linux** (optional, for better development experience)

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx
```

### macOS
```bash
# Install Homebrew first: https://brew.sh
brew install python@3.9 node
```

## Troubleshooting

### Common Issues

#### OpenCV Installation Issues
```bash
# If opencv-python fails to install
pip install opencv-python-headless==4.8.1.78
```

#### Node.js Version Issues
```bash
# Use Node Version Manager
# Windows: https://github.com/coreybutler/nvm-windows
# Linux/Mac: https://github.com/nvm-sh/nvm

nvm install 18
nvm use 18
```

#### Python Virtual Environment Issues
```bash
# If venv creation fails
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m virtualenv venv
```

#### Permission Issues (Linux/Mac)
```bash
# If permission denied
sudo chown -R $USER:$USER .
chmod +x setup.sh
```

### Performance Optimization

#### For Large Images
- Increase system RAM (8GB+ recommended)
- Use SSD storage for faster I/O
- Consider GPU acceleration for future AI features

#### For Production
- Use Redis for caching
- Implement Celery for background processing
- Use nginx for static file serving
- Configure proper logging

## Version Compatibility

| Component | Minimum | Recommended | Tested |
|-----------|---------|-------------|--------|
| Python | 3.9 | 3.11 | 3.9-3.11 |
| Node.js | 16 | 18 | 16-20 |
| npm | 8 | 9 | 8-10 |
| Docker | 20 | 24 | 20-24 |

## Security Considerations

### Production Deployment
- Use environment variables for sensitive data
- Implement rate limiting
- Add HTTPS/SSL certificates
- Configure CORS properly
- Validate all file uploads
- Implement user authentication (if needed)

### File Upload Security
- Limit file sizes (current: 10MB)
- Validate file types
- Scan for malware (recommended)
- Use secure file storage (AWS S3, etc.)

## License Requirements

All dependencies are open source with permissive licenses:
- MIT License: React, FastAPI, most packages
- BSD License: NumPy, OpenCV
- Apache 2.0: Some utility packages

No commercial licenses required for development or production use.
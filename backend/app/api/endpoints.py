from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import Response
import cv2
import numpy as np
import json
import time
from typing import Optional

from ..processors.enhanced_a24_processor import EnhancedA24StyleProcessor
from ..processors.style_presets import A24StylePresets
from ..utils.image_utils import validate_image, prepare_image_response, resize_image_if_needed
from ..models.schemas import StylesResponse, ProcessingResponse, HealthResponse
from ..config import settings

# Initialize router
router = APIRouter()

# Initialize enhanced processor
processor = EnhancedA24StyleProcessor(settings.ASSETS_PATH)

@router.get("/styles/")
async def get_available_styles():
    """Get list of available A24 styles"""
    try:
        styles = processor.get_available_styles()
        style_info = processor.get_style_info()
        return {
            "styles": styles,
            "style_info": style_info
        }
    except Exception as e:
        # Fallback to original presets
        presets = A24StylePresets.get_all_presets()
        return {
            "styles": list(presets.keys()),
            "style_info": presets
        }

@router.get("/styles/{style_name}/")
async def get_style_preset(style_name: str):
    """Get specific style preset details"""
    try:
        style_info = processor.get_style_info()
        if style_name not in style_info:
            raise HTTPException(status_code=404, detail="Style not found")
        return style_info[style_name]
    except Exception as e:
        # Fallback to original presets
        preset = A24StylePresets.get_preset(style_name)
        if not preset:
            raise HTTPException(status_code=404, detail="Style not found")
        return preset

@router.post("/process-image/")
async def process_image(
    image: UploadFile = File(...),
    style: str = Form(...),
    custom_settings: Optional[str] = Form(None)
):
    """Process image with A24 style"""
    start_time = time.time()
    
    try:
        # Validate uploaded image
        if not validate_image(image):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Read and decode image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        
        # Resize if too large
        cv_image = resize_image_if_needed(cv_image, settings.MAX_IMAGE_DIMENSION)
        
        # Parse custom settings if provided
        settings_dict = None
        if custom_settings:
            try:
                settings_dict = json.loads(custom_settings)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid custom settings JSON")
        
        # Process image with AI
        result_image = await processor.process_image_array_async(cv_image, style, settings_dict)
        
        # Prepare response
        processing_time = time.time() - start_time
        print(f"Total processing time: {processing_time:.2f} seconds")
        
        return prepare_image_response(result_image, quality=settings.DEFAULT_JPEG_QUALITY)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Store for tracking async jobs (in production, use Redis)
job_store = {}

@router.post("/process-image-async/")
async def process_image_async(
    image: UploadFile = File(...),
    style: str = Form(...),
    custom_settings: Optional[str] = Form(None)
):
    """Start asynchronous image processing with progress tracking"""
    try:
        # Validate uploaded image
        if not validate_image(image):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Generate job ID
        import uuid
        job_id = str(uuid.uuid4())
        
        # Store initial job status
        job_store[job_id] = {
            'status': 'queued',
            'progress': 0,
            'message': 'Processing queued...',
            'result': None,
            'error': None
        }
        
        # Read and decode image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Could not decode image")
        
        # Resize if too large
        cv_image = resize_image_if_needed(cv_image, settings.MAX_IMAGE_DIMENSION)
        
        # Parse custom settings
        settings_dict = None
        if custom_settings:
            try:
                settings_dict = json.loads(custom_settings)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid custom settings JSON")
        
        # Start background processing
        import asyncio
        asyncio.create_task(process_image_background(job_id, cv_image, style, settings_dict))
        
        return {"job_id": job_id, "status": "queued"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not start processing: {str(e)}")

async def process_image_background(job_id: str, image: np.ndarray, style: str, settings_dict: dict):
    """Background task for async image processing"""
    try:
        async def progress_callback(progress: int, message: str):
            job_store[job_id] = {
                'status': 'processing',
                'progress': progress,
                'message': message,
                'result': None,
                'error': None
            }
        
        # Process image with progress tracking
        result_image = await processor.process_image_array_async(
            image, style, settings_dict, progress_callback
        )
        
        # Convert result to base64 for storage
        from ..utils.image_utils import numpy_to_base64
        result_base64 = numpy_to_base64(result_image)
        
        # Store completed result
        job_store[job_id] = {
            'status': 'completed',
            'progress': 100,
            'message': 'Processing completed successfully!',
            'result': result_base64,
            'error': None
        }
        
    except Exception as e:
        # Store error result
        job_store[job_id] = {
            'status': 'failed',
            'progress': 0,
            'message': f'Processing failed: {str(e)}',
            'result': None,
            'error': str(e)
        }

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get status of async processing job"""
    if job_id not in job_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_store[job_id]

@router.get("/health/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check if AI processor is working
        styles = processor.get_available_styles()
        return HealthResponse(
            status="healthy",
            processor=f"ai_ready_with_{len(styles)}_styles",
            version=settings.VERSION
        )
    except Exception as e:
        return HealthResponse(
            status="degraded",
            processor=f"ai_error_{str(e)}",
            version=settings.VERSION
        )
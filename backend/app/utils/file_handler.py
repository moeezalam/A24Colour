import os
import shutil
import tempfile
from typing import Optional
from fastapi import UploadFile
import aiofiles

class FileHandler:
    """Handle file operations for image processing"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
    
    async def save_upload_file(self, upload_file: UploadFile, destination: str) -> str:
        """Save uploaded file to destination"""
        try:
            async with aiofiles.open(destination, 'wb') as f:
                content = await upload_file.read()
                await f.write(content)
            return destination
        except Exception as e:
            raise Exception(f"Could not save file: {e}")
    
    def create_temp_file(self, suffix: str = '.jpg') -> str:
        """Create temporary file path"""
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix, 
            dir=self.temp_dir, 
            delete=False
        )
        temp_file.close()
        return temp_file.name
    
    def cleanup_file(self, file_path: str) -> bool:
        """Remove file if it exists"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")
            return False
    
    def ensure_directory(self, directory: str) -> bool:
        """Ensure directory exists"""
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False
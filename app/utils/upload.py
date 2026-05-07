import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file):
    """Save uploaded image file and return filename."""
    if not file or not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.instance_path, '..', current_app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # Optimize image
    try:
        optimize_image(file_path)
    except Exception as e:
        current_app.logger.error(f"Error optimizing image {filename}: {e}")
    
    return filename


def optimize_image(file_path, max_width=1200, max_height=630, quality=85):
    """Optimize image size and quality."""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
    
    except Exception as e:
        current_app.logger.error(f"Error optimizing image {file_path}: {e}")


def delete_image(filename):
    """Delete image file from storage."""
    if not filename:
        return
    
    try:
        upload_dir = os.path.join(current_app.instance_path, '..', current_app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(upload_dir, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
    
    except Exception as e:
        current_app.logger.error(f"Error deleting image {filename}: {e}")


def get_image_url(filename):
    """Get URL for uploaded image."""
    if not filename:
        return None
    
    return f"/static/uploads/{filename}"


def create_thumbnail(file_path, size=(300, 200)):
    """Create thumbnail version of image."""
    try:
        filename, ext = os.path.splitext(file_path)
        thumbnail_path = f"{filename}_thumb{ext}"
        
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
        
        return os.path.basename(thumbnail_path)
    
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail for {file_path}: {e}")
        return None


def get_file_size(file_path):
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def validate_image(file):
    """Validate uploaded image file."""
    if not file:
        return False, "No file provided"
    
    if not allowed_file(file.filename):
        return False, "File type not allowed"
    
    # Check file size (10MB limit)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > current_app.config.get('MAX_CONTENT_LENGTH', 10485760):
        return False, "File too large"
    
    # Validate image format
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)  # Reset file pointer
        return True, "Valid image"
    except Exception:
        return False, "Invalid image format"
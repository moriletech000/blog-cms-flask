import os
from PIL import Image
from flask import current_app
from app.extensions import celery, db
from app.models.post import Post


@celery.task(bind=True, max_retries=3)
def process_cover_image(self, post_id):
    """Process cover image: resize and generate WebP version."""
    try:
        post = Post.query.get(post_id)
        if not post or not post.cover_image:
            return f"Post {post_id} not found or no cover image"
        
        # Get file paths
        upload_dir = os.path.join(current_app.instance_path, '..', current_app.config['UPLOAD_FOLDER'])
        image_path = os.path.join(upload_dir, post.cover_image)
        
        if not os.path.exists(image_path):
            return f"Image file {post.cover_image} not found"
        
        # Process main image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize to max 1200x630 maintaining aspect ratio
            max_size = (1200, 630)
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized JPEG (overwrite original)
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            
            # Generate WebP version at 800x420
            webp_size = (800, 420)
            webp_img = img.copy()
            webp_img.thumbnail(webp_size, Image.Resampling.LANCZOS)
            
            # Create WebP filename
            filename_without_ext = os.path.splitext(post.cover_image)[0]
            webp_filename = f"{filename_without_ext}.webp"
            webp_path = os.path.join(upload_dir, webp_filename)
            
            # Save WebP version
            webp_img.save(webp_path, 'WEBP', quality=80, optimize=True)
            
            # Update post with WebP filename
            post.cover_webp = webp_filename
            db.session.commit()
        
        return f"Processed cover image for post {post_id}: {post.cover_image} -> {webp_filename}"
    
    except Exception as exc:
        current_app.logger.error(f"Error processing cover image for post {post_id}: {exc}")
        raise self.retry(countdown=60, exc=exc)


@celery.task(bind=True)
def cleanup_orphaned_images(self):
    """Clean up orphaned image files."""
    try:
        upload_dir = os.path.join(current_app.instance_path, '..', current_app.config['UPLOAD_FOLDER'])
        
        if not os.path.exists(upload_dir):
            return "Upload directory does not exist"
        
        # Get all image files in upload directory
        image_files = []
        for filename in os.listdir(upload_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                image_files.append(filename)
        
        # Get all image filenames referenced in database
        referenced_images = set()
        posts = Post.query.all()
        for post in posts:
            if post.cover_image:
                referenced_images.add(post.cover_image)
            if post.cover_webp:
                referenced_images.add(post.cover_webp)
        
        # Find orphaned files
        orphaned_files = []
        for filename in image_files:
            if filename not in referenced_images:
                orphaned_files.append(filename)
        
        # Delete orphaned files
        deleted_count = 0
        for filename in orphaned_files:
            try:
                file_path = os.path.join(upload_dir, filename)
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                current_app.logger.error(f"Error deleting orphaned file {filename}: {e}")
        
        return f"Cleaned up {deleted_count} orphaned image files"
    
    except Exception as exc:
        current_app.logger.error(f"Error cleaning up orphaned images: {exc}")
        return f"Error: {exc}"


@celery.task(bind=True)
def generate_image_thumbnails(self, force_regenerate=False):
    """Generate thumbnails for all post images."""
    try:
        posts = Post.query.filter(Post.cover_image.isnot(None)).all()
        processed_count = 0
        
        upload_dir = os.path.join(current_app.instance_path, '..', current_app.config['UPLOAD_FOLDER'])
        
        for post in posts:
            try:
                # Skip if WebP already exists and not forcing regeneration
                if post.cover_webp and not force_regenerate:
                    webp_path = os.path.join(upload_dir, post.cover_webp)
                    if os.path.exists(webp_path):
                        continue
                
                # Process the image
                process_cover_image.delay(str(post.id))
                processed_count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error processing image for post {post.id}: {e}")
        
        return f"Queued thumbnail generation for {processed_count} images"
    
    except Exception as exc:
        current_app.logger.error(f"Error generating thumbnails: {exc}")
        return f"Error: {exc}"


@celery.task(bind=True)
def optimize_all_images(self):
    """Optimize all existing images."""
    try:
        upload_dir = os.path.join(current_app.instance_path, '..', current_app.config['UPLOAD_FOLDER'])
        
        if not os.path.exists(upload_dir):
            return "Upload directory does not exist"
        
        optimized_count = 0
        
        for filename in os.listdir(upload_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    file_path = os.path.join(upload_dir, filename)
                    
                    with Image.open(file_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # Save with optimization
                        img.save(file_path, 'JPEG', quality=85, optimize=True)
                        optimized_count += 1
                
                except Exception as e:
                    current_app.logger.error(f"Error optimizing image {filename}: {e}")
        
        return f"Optimized {optimized_count} images"
    
    except Exception as exc:
        current_app.logger.error(f"Error optimizing images: {exc}")
        return f"Error: {exc}"
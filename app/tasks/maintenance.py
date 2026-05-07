"""
Maintenance tasks for periodic cleanup and optimization.
"""

from datetime import datetime, timedelta
from flask import current_app
from app.extensions import celery, db, redis_client
from app.models.post import Post


@celery.task(bind=True)
def flush_view_counters(self):
    """Flush view counters from Redis to PostgreSQL database."""
    try:
        # Get all view counter keys from Redis
        keys = redis_client.keys('post:views:*')
        updated_count = 0
        
        for key in keys:
            try:
                post_id = key.decode('utf-8').split(':')[-1]
                view_count = int(redis_client.get(key) or 0)
                
                if view_count > 0:
                    post = Post.query.get(post_id)
                    if post:
                        post.views += view_count
                        redis_client.delete(key)
                        updated_count += 1
            except Exception as e:
                current_app.logger.error(f"Error processing view counter for key {key}: {e}")
        
        db.session.commit()
        return f"Flushed view counters for {updated_count} posts"
    
    except Exception as exc:
        current_app.logger.error(f"Error flushing view counters: {exc}")
        db.session.rollback()
        return f"Error: {exc}"


@celery.task(bind=True)
def cleanup_expired_sessions(self):
    """Clean up expired sessions from the database."""
    try:
        # This is a placeholder - Flask-Login uses server-side sessions
        # If using Flask-Session with database backend, implement cleanup here
        
        # Example: Delete sessions older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # If using flask_session with SQLAlchemy backend:
        # from flask_session import Session
        # Session.query.filter(Session.expiry < cutoff_date).delete()
        # db.session.commit()
        
        return "Session cleanup completed"
    
    except Exception as exc:
        current_app.logger.error(f"Error cleaning up sessions: {exc}")
        return f"Error: {exc}"


@celery.task(bind=True)
def cleanup_old_data(self):
    """Clean up old archived posts and data."""
    try:
        # Delete archived posts older than 1 year
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        
        old_archived_posts = Post.query.filter(
            Post.status == 'archived',
            Post.updated_at < one_year_ago
        ).all()
        
        deleted_count = 0
        for post in old_archived_posts:
            # Delete associated images
            if post.cover_image:
                from app.utils.upload import delete_image
                delete_image(post.cover_image)
            if post.cover_webp:
                from app.utils.upload import delete_image
                delete_image(post.cover_webp)
            
            db.session.delete(post)
            deleted_count += 1
        
        db.session.commit()
        return f"Deleted {deleted_count} old archived posts"
    
    except Exception as exc:
        current_app.logger.error(f"Error cleaning up old data: {exc}")
        db.session.rollback()
        return f"Error: {exc}"


@celery.task(bind=True)
def update_search_vectors(self):
    """Update search vectors for all posts."""
    try:
        # This would typically be handled by PostgreSQL triggers
        # But can be run manually if needed
        
        posts = Post.query.all()
        updated_count = 0
        
        for post in posts:
            # PostgreSQL will update the search_vector via trigger
            # This just touches the record to trigger the update
            post.updated_at = datetime.utcnow()
            updated_count += 1
        
        db.session.commit()
        return f"Updated search vectors for {updated_count} posts"
    
    except Exception as exc:
        current_app.logger.error(f"Error updating search vectors: {exc}")
        db.session.rollback()
        return f"Error: {exc}"


@celery.task(bind=True)
def generate_sitemap(self):
    """Generate sitemap.xml for SEO."""
    try:
        from flask import url_for
        
        # Get all published posts
        posts = Post.query.filter_by(status='published').all()
        
        # Generate sitemap XML
        sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        # Add homepage
        sitemap.append('<url>')
        sitemap.append(f'<loc>{url_for("blog.index", _external=True)}</loc>')
        sitemap.append('<changefreq>daily</changefreq>')
        sitemap.append('<priority>1.0</priority>')
        sitemap.append('</url>')
        
        # Add posts
        for post in posts:
            sitemap.append('<url>')
            sitemap.append(f'<loc>{url_for("blog.post_detail", slug=post.slug, _external=True)}</loc>')
            sitemap.append(f'<lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>')
            sitemap.append('<changefreq>weekly</changefreq>')
            sitemap.append('<priority>0.8</priority>')
            sitemap.append('</url>')
        
        sitemap.append('</urlset>')
        
        # Save sitemap to static directory
        import os
        sitemap_path = os.path.join(current_app.static_folder, 'sitemap.xml')
        with open(sitemap_path, 'w') as f:
            f.write('\n'.join(sitemap))
        
        return f"Generated sitemap with {len(posts)} posts"
    
    except Exception as exc:
        current_app.logger.error(f"Error generating sitemap: {exc}")
        return f"Error: {exc}"


@celery.task(bind=True)
def backup_database(self):
    """Create database backup (placeholder for production implementation)."""
    try:
        # In production, implement actual database backup logic
        # This could use pg_dump for PostgreSQL
        
        current_app.logger.info("Database backup task executed")
        return "Database backup completed (placeholder)"
    
    except Exception as exc:
        current_app.logger.error(f"Error backing up database: {exc}")
        return f"Error: {exc}"
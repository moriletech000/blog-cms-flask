#!/usr/bin/env python
"""
Simplified demo runner for Blog CMS
Works with SQLite by temporarily disabling PostgreSQL-specific features
"""

import os
import sys

print("=" * 60)
print("Blog CMS - Simplified Demo Mode")
print("=" * 60)
print()

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['DATABASE_URL'] = 'sqlite:///blog_demo.db'
os.environ['FLASK_SECRET_KEY'] = 'demo-secret-key'
os.environ['JWT_SECRET_KEY'] = 'demo-jwt-secret'
os.environ['CACHE_TYPE'] = 'SimpleCache'
os.environ['RATELIMIT_ENABLED'] = 'False'

print("Setting up simplified demo environment...")
print()

# Temporarily patch the Post model to work with SQLite
import app.models.post as post_module
from sqlalchemy import Text

# Replace TSVECTOR with Text for SQLite compatibility
original_post_class = post_module.Post

class PatchedPost(original_post_class):
    """Patched Post model for SQLite"""
    __tablename__ = 'posts'
    
    # Override search_vector to use Text instead of TSVECTOR
    from sqlalchemy.orm import mapped_column
    search_vector = mapped_column(Text, nullable=True)

# Replace the Post class
post_module.Post = PatchedPost

print("✓ Models patched for SQLite compatibility")

# Now import the app
from app import create_app
from app.extensions import db
from app.models import User, Category, Tag
from werkzeug.security import generate_password_hash
from datetime import datetime
from slugify import slugify

print("✓ Modules imported")
print()

try:
    # Create app
    app = create_app('development')
    
    with app.app_context():
        # Drop and recreate tables
        print("Creating database...")
        db.drop_all()
        db.create_all()
        print("✓ Database created")
        print()
        
        print("Adding sample data...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@blog.com',
            password_hash=generate_password_hash('admin123', method='pbkdf2:sha256', salt_length=16),
            role='admin',
            is_active=True,
            is_confirmed=True,
            confirmed_at=datetime.utcnow(),
            bio='System Administrator'
        )
        db.session.add(admin)
        
        # Create editor user
        editor = User(
            username='editor',
            email='editor@blog.com',
            password_hash=generate_password_hash('editor123', method='pbkdf2:sha256', salt_length=16),
            role='editor',
            is_active=True,
            is_confirmed=True,
            confirmed_at=datetime.utcnow(),
            bio='Content Editor'
        )
        db.session.add(editor)
        
        # Create categories
        categories = [
            Category(name='Technology', slug='technology', description='Tech news and tutorials', color='#3b82f6'),
            Category(name='Programming', slug='programming', description='Coding tips', color='#10b981'),
            Category(name='Web Development', slug='web-development', description='Frontend and backend', color='#f59e0b'),
        ]
        for cat in categories:
            db.session.add(cat)
        
        # Create tags
        tags = [
            Tag(name='Python', slug='python'),
            Tag(name='Flask', slug='flask'),
            Tag(name='JavaScript', slug='javascript'),
            Tag(name='React', slug='react'),
        ]
        for tag in tags:
            db.session.add(tag)
        
        db.session.flush()
        
        # Create sample posts
        posts_data = [
            {
                'title': 'Welcome to Blog CMS',
                'body': '<h2>Getting Started</h2><p>Welcome to your new blog! This is a sample post to help you get started.</p><p>You can create, edit, and manage posts from the admin panel.</p><h3>Features</h3><ul><li>Rich text editing</li><li>Categories and tags</li><li>Comment system</li><li>User management</li></ul>',
                'category': categories[0],
                'tags': [tags[0], tags[1]]
            },
            {
                'title': 'Building Modern Web Applications',
                'body': '<p>Modern web applications require a solid foundation. In this post, we explore best practices for building scalable web apps.</p><p>Key considerations include:</p><ul><li>Security</li><li>Performance</li><li>User experience</li><li>Maintainability</li></ul>',
                'category': categories[2],
                'tags': [tags[2], tags[3]]
            },
            {
                'title': 'Python Tips and Tricks',
                'body': '<p>Python is a versatile programming language. Here are some tips to improve your Python code:</p><ol><li>Use list comprehensions</li><li>Leverage built-in functions</li><li>Write clean, readable code</li><li>Test your code</li></ol>',
                'category': categories[1],
                'tags': [tags[0]]
            }
        ]
        
        for post_data in posts_data:
            post = PatchedPost(
                title=post_data['title'],
                slug=slugify(post_data['title']),
                body=post_data['body'],
                excerpt=post_data['body'][:200] + '...',
                status='published',
                author=admin,
                category=post_data['category'],
                published_at=datetime.utcnow(),
                views=0
            )
            for tag in post_data['tags']:
                post.tags.append(tag)
            db.session.add(post)
        
        db.session.commit()
        print("✓ Sample data added")
        print()
        
        print("=" * 60)
        print("🚀 Demo Server Ready!")
        print("=" * 60)
        print()
        print("Access the application at:")
        print("  🌐 Blog:      http://localhost:5000")
        print("  👤 Admin:     http://localhost:5000/admin")
        print("  📚 API Docs:  http://localhost:5000/api/v1/docs")
        print()
        print("Login Credentials:")
        print("  Admin:")
        print("    📧 Email:    admin@blog.com")
        print("    🔑 Password: admin123")
        print()
        print("  Editor:")
        print("    📧 Email:    editor@blog.com")
        print("    🔑 Password: editor123")
        print()
        print("⚠️  Demo Mode Limitations:")
        print("   • Using SQLite (not PostgreSQL)")
        print("   • No full-text search")
        print("   • No Redis caching")
        print("   • No background tasks")
        print("   • No email sending")
        print()
        print("For full features, use Docker or install PostgreSQL + Redis")
        print("See WINDOWS_SETUP.md for instructions")
        print()
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        print()
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
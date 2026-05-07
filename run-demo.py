#!/usr/bin/env python
"""
Quick demo runner for Blog CMS without Docker
Uses SQLite instead of PostgreSQL for simplicity
"""

import os
import sys

print("=" * 50)
print("Blog CMS - Quick Demo Mode")
print("=" * 50)
print()

# Set environment variables for demo mode
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'
os.environ['DATABASE_URL'] = 'sqlite:///blog_demo.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'  # Will gracefully fail if not available
os.environ['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
os.environ['FLASK_SECRET_KEY'] = 'demo-secret-key-not-for-production'
os.environ['JWT_SECRET_KEY'] = 'demo-jwt-secret-key'

# Disable features that require Redis/Celery
os.environ['CACHE_TYPE'] = 'SimpleCache'
os.environ['RATELIMIT_ENABLED'] = 'False'

print("✓ Environment configured for demo mode")
print("✓ Using SQLite database (blog_demo.db)")
print()

# Import Flask app
try:
    from app import create_app
    from app.extensions import db
    from app.models import User, Category, Post, Tag
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    print("✓ Modules imported successfully")
    print()
    
    # Create app
    app = create_app('development')
    
    with app.app_context():
        # Create tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        print()
        
        # Check if already seeded
        if User.query.count() == 0:
            print("Seeding database with sample data...")
            
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
            
            # Create a category
            category = Category(
                name='Technology',
                slug='technology',
                description='Tech news and tutorials',
                color='#3b82f6'
            )
            db.session.add(category)
            
            # Create a sample post
            post = Post(
                title='Welcome to Blog CMS',
                slug='welcome-to-blog-cms',
                body='<p>Welcome to your new blog! This is a sample post to get you started.</p><p>You can create, edit, and manage posts from the admin panel.</p>',
                excerpt='Welcome to your new blog! This is a sample post to get you started.',
                status='published',
                author=admin,
                category=category,
                published_at=datetime.utcnow()
            )
            db.session.add(post)
            
            db.session.commit()
            print("✓ Database seeded with sample data")
            print()
        else:
            print("✓ Database already contains data")
            print()
        
        print("=" * 50)
        print("Demo Server Starting!")
        print("=" * 50)
        print()
        print("Access the application at:")
        print("  🌐 Blog:      http://localhost:5000")
        print("  👤 Admin:     http://localhost:5000/admin")
        print("  📚 API Docs:  http://localhost:5000/api/v1/docs")
        print()
        print("Default Admin Login:")
        print("  📧 Email:    admin@blog.com")
        print("  🔑 Password: admin123")
        print()
        print("⚠️  Note: This is demo mode with limited features:")
        print("   - Using SQLite (not PostgreSQL)")
        print("   - No Redis caching")
        print("   - No background tasks (Celery)")
        print("   - No email sending")
        print()
        print("For full features, use Docker or install PostgreSQL + Redis")
        print("See WINDOWS_SETUP.md for instructions")
        print()
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        print()
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=True)

except ImportError as e:
    print(f"✗ Error importing modules: {e}")
    print()
    print("Please install dependencies first:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
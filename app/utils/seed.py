import uuid
from datetime import datetime, timedelta
from faker import Faker
from werkzeug.security import generate_password_hash
from slugify import slugify
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post
from app.models.comment import Comment


fake = Faker()


def seed_database():
    """Seed the database with initial data."""
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@blog.com',
        password_hash=generate_password_hash('admin123', method='pbkdf2:sha256', salt_length=16),
        role='admin',
        is_active=True,
        is_confirmed=True,
        confirmed_at=datetime.utcnow(),
        bio='System administrator'
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
        bio='Content editor'
    )
    db.session.add(editor)
    
    # Create sample readers
    readers = []
    for i in range(3):
        reader = User(
            username=fake.user_name(),
            email=fake.email(),
            password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
            role='reader',
            is_active=True,
            is_confirmed=True,
            confirmed_at=datetime.utcnow(),
            bio=fake.text(max_nb_chars=200)
        )
        readers.append(reader)
        db.session.add(reader)
    
    # Create categories
    categories_data = [
        {'name': 'Technology', 'description': 'Latest tech news and tutorials', 'color': '#3b82f6'},
        {'name': 'Programming', 'description': 'Coding tips and best practices', 'color': '#10b981'},
        {'name': 'Web Development', 'description': 'Frontend and backend development', 'color': '#f59e0b'},
        {'name': 'Data Science', 'description': 'Analytics and machine learning', 'color': '#8b5cf6'},
        {'name': 'DevOps', 'description': 'Deployment and infrastructure', 'color': '#ef4444'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(
            name=cat_data['name'],
            slug=slugify(cat_data['name']),
            description=cat_data['description'],
            color=cat_data['color']
        )
        categories.append(category)
        db.session.add(category)
    
    # Create tags
    tag_names = [
        'Python', 'JavaScript', 'React', 'Flask', 'Django', 'Node.js',
        'Docker', 'Kubernetes', 'AWS', 'Machine Learning', 'AI',
        'Frontend', 'Backend', 'API', 'Database', 'PostgreSQL'
    ]
    
    tags = []
    for tag_name in tag_names:
        tag = Tag(
            name=tag_name,
            slug=slugify(tag_name)
        )
        tags.append(tag)
        db.session.add(tag)
    
    db.session.flush()  # Get IDs for relationships
    
    # Create sample posts
    authors = [admin, editor] + readers
    
    for i in range(15):
        # Random publish date in the last 30 days
        days_ago = fake.random_int(min=0, max=30)
        published_at = datetime.utcnow() - timedelta(days=days_ago)
        
        title = fake.sentence(nb_words=6).rstrip('.')
        body_paragraphs = [fake.paragraph(nb_sentences=5) for _ in range(fake.random_int(min=3, max=8))]
        body = '<p>' + '</p><p>'.join(body_paragraphs) + '</p>'
        
        post = Post(
            title=title,
            slug=slugify(title),
            body=body,
            excerpt=fake.text(max_nb_chars=200),
            status='published' if i < 12 else 'draft',  # Most posts published
            views=fake.random_int(min=10, max=1000),
            author_id=fake.choice(authors).id,
            category_id=fake.choice(categories).id,
            published_at=published_at if i < 12 else None,
            created_at=published_at - timedelta(hours=fake.random_int(min=1, max=24))
        )
        
        # Add random tags (1-4 tags per post)
        post_tags = fake.random_elements(elements=tags, length=fake.random_int(min=1, max=4), unique=True)
        for tag in post_tags:
            post.tags.append(tag)
        
        db.session.add(post)
    
    db.session.flush()  # Get post IDs
    
    # Create sample comments
    published_posts = Post.query.filter_by(status='published').all()
    
    for _ in range(25):
        post = fake.choice(published_posts)
        author = fake.choice(readers + [admin, editor])
        
        comment = Comment(
            body=fake.paragraph(nb_sentences=fake.random_int(min=1, max=4)),
            author_id=author.id,
            post_id=post.id,
            is_approved=True,
            created_at=fake.date_time_between(
                start_date=post.published_at,
                end_date=datetime.utcnow()
            )
        )
        db.session.add(comment)
    
    # Create some replies
    comments = Comment.query.all()
    for _ in range(10):
        parent_comment = fake.choice(comments)
        author = fake.choice(readers + [admin, editor])
        
        reply = Comment(
            body=fake.paragraph(nb_sentences=fake.random_int(min=1, max=3)),
            author_id=author.id,
            post_id=parent_comment.post_id,
            parent_id=parent_comment.id,
            is_approved=True,
            created_at=fake.date_time_between(
                start_date=parent_comment.created_at,
                end_date=datetime.utcnow()
            )
        )
        db.session.add(reply)
    
    db.session.commit()
    print("Database seeded successfully!")
    print(f"Created:")
    print(f"  - {User.query.count()} users")
    print(f"  - {Category.query.count()} categories")
    print(f"  - {Tag.query.count()} tags")
    print(f"  - {Post.query.count()} posts")
    print(f"  - {Comment.query.count()} comments")
    print(f"\nAdmin login: admin@blog.com / admin123")
    print(f"Editor login: editor@blog.com / editor123")
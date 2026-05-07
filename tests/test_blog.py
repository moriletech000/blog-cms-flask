"""
Tests for blog functionality.
"""

import pytest
from tests.factories import UserFactory, PostFactory, CategoryFactory, CommentFactory
from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment


def test_index_shows_published_posts(client, db):
    """Test that index page shows published posts."""
    # Create published and draft posts
    published_post = PostFactory(status='published')
    draft_post = PostFactory(status='draft')
    db.session.commit()
    
    response = client.get('/')
    
    assert response.status_code == 200
    assert published_post.title.encode() in response.data
    assert draft_post.title.encode() not in response.data


def test_post_detail_increments_view(client, db, app):
    """Test that viewing a post increments view counter."""
    from app.extensions import redis_client
    
    post = PostFactory(status='published', views=0)
    db.session.commit()
    
    # View post twice
    with app.app_context():
        client.get(f'/post/{post.slug}')
        client.get(f'/post/{post.slug}')
        
        # Check Redis counter
        redis_key = f'post:views:{post.id}'
        view_count = int(redis_client.get(redis_key) or 0)
        assert view_count == 2


def test_like_toggle(auth_client, db):
    """Test liking and unliking a post."""
    post = PostFactory(status='published')
    db.session.commit()
    
    # Like post
    response = auth_client.post(f'/post/{post.slug}/like')
    assert response.status_code == 200
    data = response.get_json()
    assert data['liked'] == True
    assert data['count'] == 1
    
    # Unlike post
    response = auth_client.post(f'/post/{post.slug}/like')
    assert response.status_code == 200
    data = response.get_json()
    assert data['liked'] == False
    assert data['count'] == 0


def test_like_requires_login(client, db):
    """Test that liking requires authentication."""
    post = PostFactory(status='published')
    db.session.commit()
    
    response = client.post(f'/post/{post.slug}/like')
    assert response.status_code == 302  # Redirect to login


def test_comment_creates_notification_task(auth_client, db, mocker):
    """Test that posting a comment triggers notification task."""
    # Mock Celery task
    mock_task = mocker.patch('app.tasks.email.send_comment_notification.delay')
    
    post = PostFactory(status='published')
    db.session.commit()
    
    # Post comment
    response = auth_client.post(f'/post/{post.slug}/comment', data={
        'body': 'This is a test comment'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify comment was created
    comment = Comment.query.filter_by(post_id=post.id).first()
    assert comment is not None
    assert comment.body == 'This is a test comment'
    
    # Verify notification task was called
    mock_task.assert_called_once()


def test_search_returns_results(client, db):
    """Test search functionality."""
    # Create posts with specific content
    post1 = PostFactory(title='Python Programming Guide', status='published')
    post2 = PostFactory(title='JavaScript Tutorial', status='published')
    db.session.commit()
    
    # Search for Python
    response = client.get('/search?q=Python')
    
    assert response.status_code == 200
    assert b'Python' in response.data


def test_category_filter(client, db):
    """Test filtering posts by category."""
    category = CategoryFactory(name='Technology')
    post1 = PostFactory(status='published', category=category)
    post2 = PostFactory(status='published')  # Different category
    db.session.commit()
    
    response = client.get(f'/category/{category.slug}')
    
    assert response.status_code == 200
    assert post1.title.encode() in response.data


def test_tag_filter(client, db):
    """Test filtering posts by tag."""
    from tests.factories import TagFactory
    
    tag = TagFactory(name='Python')
    post = PostFactory(status='published')
    post.tags.append(tag)
    db.session.commit()
    
    response = client.get(f'/tag/{tag.slug}')
    
    assert response.status_code == 200
    assert post.title.encode() in response.data


def test_comment_requires_confirmation(client, db):
    """Test that commenting requires confirmed email."""
    from werkzeug.security import generate_password_hash
    from app.models.user import User
    
    # Create unconfirmed user
    user = User(
        username='unconfirmed',
        email='unconfirmed@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True,
        is_confirmed=False
    )
    db.session.add(user)
    
    post = PostFactory(status='published')
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'email': 'unconfirmed@example.com',
        'password': 'password123'
    })
    
    # Try to comment
    response = client.post(f'/post/{post.slug}/comment', data={
        'body': 'Test comment'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'confirm your email' in response.data.lower()


def test_post_detail_404_for_draft(client, db):
    """Test that draft posts return 404 on detail page."""
    post = PostFactory(status='draft')
    db.session.commit()
    
    response = client.get(f'/post/{post.slug}')
    
    assert response.status_code == 404


def test_pagination(client, db):
    """Test post pagination."""
    # Create 15 posts (more than one page)
    for i in range(15):
        PostFactory(status='published')
    db.session.commit()
    
    # Get first page
    response = client.get('/')
    assert response.status_code == 200
    assert b'Next' in response.data or b'next' in response.data
    
    # Get second page
    response = client.get('/?page=2')
    assert response.status_code == 200
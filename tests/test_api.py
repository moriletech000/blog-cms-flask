"""
Tests for REST API functionality.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from tests.factories import UserFactory, PostFactory, CategoryFactory, TagFactory
from app.models.post import Post


def get_auth_token(app, user):
    """Helper to generate JWT token for user."""
    payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')


def test_get_posts_no_auth(client, db):
    """Test getting posts without authentication."""
    post = PostFactory(status='published')
    db.session.commit()
    
    response = client.get('/api/v1/posts')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert 'meta' in data
    assert len(data['data']) > 0


def test_create_post_requires_editor(client, app, db):
    """Test that creating post requires editor role."""
    # Reader user
    reader = UserFactory(role='reader')
    db.session.commit()
    
    token = get_auth_token(app, reader)
    
    response = client.post('/api/v1/posts', 
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Post',
            'body': 'Test content',
            'status': 'draft'
        }
    )
    
    assert response.status_code == 403


def test_create_post_with_editor(client, app, db):
    """Test creating post with editor role."""
    editor = UserFactory(role='editor')
    category = CategoryFactory()
    db.session.commit()
    
    token = get_auth_token(app, editor)
    
    response = client.post('/api/v1/posts',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'API Test Post',
            'body': '<p>Test content</p>',
            'status': 'draft',
            'category_id': str(category.id),
            'tags': ['python', 'flask']
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'API Test Post'
    assert data['slug'] == 'api-test-post'


def test_get_post_by_slug(client, db):
    """Test getting a single post by slug."""
    post = PostFactory(status='published')
    db.session.commit()
    
    response = client.get(f'/api/v1/posts/{post.slug}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == post.title
    assert data['slug'] == post.slug


def test_jwt_refresh(client, app, db):
    """Test refreshing JWT token."""
    user = UserFactory()
    db.session.commit()
    
    # Generate refresh token
    refresh_payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    refresh_token = jwt.encode(refresh_payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    response = client.post('/api/v1/auth/refresh',
        json={'refresh_token': refresh_token}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_pagination_meta(client, db):
    """Test pagination metadata in API response."""
    # Create 15 posts
    for i in range(15):
        PostFactory(status='published')
    db.session.commit()
    
    response = client.get('/api/v1/posts?page=1&per_page=5')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['meta']['per_page'] == 5
    assert data['meta']['page'] == 1
    assert data['meta']['total'] >= 15


def test_login_api(client, db):
    """Test API login endpoint."""
    from werkzeug.security import generate_password_hash
    from app.models.user import User
    
    user = User(
        username='apiuser',
        email='api@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/api/v1/auth/token',
        json={
            'email': 'api@example.com',
            'password': 'password123'
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['token_type'] == 'Bearer'


def test_get_categories(client, db):
    """Test getting all categories."""
    category1 = CategoryFactory(name='Tech')
    category2 = CategoryFactory(name='Science')
    db.session.commit()
    
    response = client.get('/api/v1/categories')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2


def test_get_tags(client, db):
    """Test getting all tags."""
    tag1 = TagFactory(name='Python')
    tag2 = TagFactory(name='Flask')
    db.session.commit()
    
    response = client.get('/api/v1/tags')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 2


def test_get_user_profile(client, app, db):
    """Test getting current user profile."""
    user = UserFactory()
    db.session.commit()
    
    token = get_auth_token(app, user)
    
    response = client.get('/api/v1/users/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == user.username
    assert data['email'] == user.email


def test_update_user_profile(client, app, db):
    """Test updating user profile."""
    user = UserFactory()
    db.session.commit()
    
    token = get_auth_token(app, user)
    
    response = client.put('/api/v1/users/me',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'bio': 'Updated bio text'
        }
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['bio'] == 'Updated bio text'


def test_add_comment_via_api(client, app, db):
    """Test adding comment via API."""
    user = UserFactory(is_confirmed=True)
    post = PostFactory(status='published')
    db.session.commit()
    
    token = get_auth_token(app, user)
    
    response = client.post(f'/api/v1/posts/{post.slug}/comments',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'body': 'API comment test'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['body'] == 'API comment test'


def test_get_post_comments(client, db):
    """Test getting comments for a post."""
    from tests.factories import CommentFactory
    
    post = PostFactory(status='published')
    comment = CommentFactory(post=post, is_approved=True)
    db.session.commit()
    
    response = client.get(f'/api/v1/posts/{post.slug}/comments')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert len(data['data']) > 0


def test_api_requires_valid_token(client, db):
    """Test that API endpoints require valid token."""
    response = client.post('/api/v1/posts',
        headers={'Authorization': 'Bearer invalid-token'},
        json={
            'title': 'Test',
            'body': 'Test'
        }
    )
    
    assert response.status_code == 401


def test_filter_posts_by_category(client, db):
    """Test filtering posts by category via API."""
    category = CategoryFactory(name='Tech')
    post = PostFactory(status='published', category=category)
    db.session.commit()
    
    response = client.get(f'/api/v1/posts?category={category.slug}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['data']) > 0
    assert data['data'][0]['category']['slug'] == category.slug
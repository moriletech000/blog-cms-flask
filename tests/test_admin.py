"""
Tests for admin functionality.
"""

import pytest
from tests.factories import PostFactory, CategoryFactory, UserFactory
from app.models.post import Post
from app.models.category import Category


def test_admin_dashboard_requires_admin(client, auth_client):
    """Test that admin dashboard requires admin role."""
    # Regular user should get 403
    response = auth_client.get('/admin/')
    assert response.status_code == 403


def test_admin_dashboard_accessible_by_admin(admin_client):
    """Test that admin can access dashboard."""
    response = admin_client.get('/admin/')
    assert response.status_code == 200
    assert b'dashboard' in response.data.lower() or b'Dashboard' in response.data


def test_create_post(admin_client, db):
    """Test creating a new post."""
    category = CategoryFactory()
    db.session.commit()
    
    response = admin_client.post('/admin/posts/new', data={
        'title': 'Test Post',
        'body': '<p>This is a test post body.</p>',
        'excerpt': 'Test excerpt',
        'status': 'draft',
        'category_id': str(category.id),
        'tags': 'python, flask'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify post was created
    post = Post.query.filter_by(title='Test Post').first()
    assert post is not None
    assert post.body == '<p>This is a test post body.</p>'
    assert post.status == 'draft'


def test_delete_post_archives_not_deletes(admin_client, db):
    """Test that deleting a post archives it."""
    post = PostFactory(status='published')
    db.session.commit()
    post_id = post.id
    
    response = admin_client.post(f'/admin/posts/{post_id}/delete', follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify post still exists but is archived
    post = Post.query.get(post_id)
    assert post is not None
    assert post.status == 'archived'


def test_publish_post(admin_client, db):
    """Test publishing a draft post."""
    post = PostFactory(status='draft', published_at=None)
    db.session.commit()
    post_id = post.id
    
    response = admin_client.post(f'/admin/posts/{post_id}/publish', follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify post is published
    post = Post.query.get(post_id)
    assert post.status == 'published'
    assert post.published_at is not None


def test_create_category(admin_client, db):
    """Test creating a new category."""
    response = admin_client.post('/admin/categories/new', data={
        'name': 'New Category',
        'description': 'Test description',
        'color': '#ff0000'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify category was created
    category = Category.query.filter_by(name='New Category').first()
    assert category is not None
    assert category.color == '#ff0000'


def test_delete_category_with_posts_fails(admin_client, db):
    """Test that deleting a category with posts fails."""
    category = CategoryFactory()
    post = PostFactory(category=category, status='published')
    db.session.commit()
    category_id = category.id
    
    response = admin_client.post(f'/admin/categories/{category_id}/delete', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Cannot delete' in response.data or b'cannot delete' in response.data
    
    # Verify category still exists
    category = Category.query.get(category_id)
    assert category is not None


def test_change_user_role(admin_client, db):
    """Test changing user role."""
    user = UserFactory(role='reader')
    db.session.commit()
    user_id = user.id
    
    response = admin_client.post(f'/admin/users/{user_id}/role', data={
        'role': 'editor'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify role was changed
    from app.models.user import User
    user = User.query.get(user_id)
    assert user.role == 'editor'


def test_toggle_user_status(admin_client, db):
    """Test activating/deactivating user."""
    user = UserFactory(is_active=True)
    db.session.commit()
    user_id = user.id
    
    response = admin_client.post(f'/admin/users/{user_id}/toggle', follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify user was deactivated
    from app.models.user import User
    user = User.query.get(user_id)
    assert user.is_active == False


def test_editor_can_create_post(editor_client, db):
    """Test that editor can create posts."""
    category = CategoryFactory()
    db.session.commit()
    
    response = editor_client.post('/admin/posts/new', data={
        'title': 'Editor Post',
        'body': '<p>Post by editor.</p>',
        'status': 'draft',
        'category_id': str(category.id)
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify post was created
    post = Post.query.filter_by(title='Editor Post').first()
    assert post is not None


def test_editor_cannot_access_user_management(editor_client):
    """Test that editor cannot access user management."""
    response = editor_client.get('/admin/users')
    assert response.status_code == 403


def test_post_slug_auto_generated(admin_client, db):
    """Test that post slug is auto-generated from title."""
    response = admin_client.post('/admin/posts/new', data={
        'title': 'My Awesome Post Title',
        'body': '<p>Content</p>',
        'status': 'draft'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify slug was generated
    post = Post.query.filter_by(title='My Awesome Post Title').first()
    assert post is not None
    assert post.slug == 'my-awesome-post-title'


def test_comment_moderation(admin_client, db):
    """Test comment approval/unapproval."""
    from tests.factories import CommentFactory
    
    comment = CommentFactory(is_approved=True)
    db.session.commit()
    comment_id = comment.id
    
    response = admin_client.post(f'/admin/comments/{comment_id}/toggle', follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify comment was unapproved
    from app.models.comment import Comment
    comment = Comment.query.get(comment_id)
    assert comment.is_approved == False
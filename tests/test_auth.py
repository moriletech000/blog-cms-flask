"""
Tests for authentication functionality.
"""

import pytest
from app.models.user import User
from app.extensions import db


def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Check user was created
    user = User.query.filter_by(email='newuser@example.com').first()
    assert user is not None
    assert user.username == 'newuser'
    assert user.is_confirmed == False


def test_register_duplicate_email(client, db):
    """Test registration with duplicate email."""
    # Create existing user
    from werkzeug.security import generate_password_hash
    user = User(
        username='existing',
        email='existing@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to register with same email
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'existing@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data


def test_login_success(client, db):
    """Test successful login."""
    from werkzeug.security import generate_password_hash
    
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Login
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_login_wrong_password(client, db):
    """Test login with wrong password."""
    from werkzeug.security import generate_password_hash
    
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Try login with wrong password
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data


def test_logout(auth_client):
    """Test logout functionality."""
    response = auth_client.get('/auth/logout', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'logged out' in response.data.lower()


def test_forgot_password(client, db):
    """Test forgot password flow."""
    from werkzeug.security import generate_password_hash
    
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Request password reset
    response = client.post('/auth/forgot-password', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_password_reset_with_valid_token(client, db, app):
    """Test password reset with valid token."""
    from werkzeug.security import generate_password_hash, check_password_hash
    from app.utils.helpers import generate_token
    
    # Create user
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('oldpassword', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Generate reset token
    with app.app_context():
        token = generate_token(user.email, salt='password-reset')
    
    # Reset password
    response = client.post(f'/auth/reset-password/{token}', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify password was changed
    user = User.query.filter_by(email='test@example.com').first()
    assert check_password_hash(user.password_hash, 'newpassword123')


def test_login_inactive_user(client, db):
    """Test login with inactive user account."""
    from werkzeug.security import generate_password_hash
    
    # Create inactive user
    user = User(
        username='inactive',
        email='inactive@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=False
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to login
    response = client.post('/auth/login', data={
        'email': 'inactive@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert b'deactivated' in response.data.lower()
"""
Pytest configuration and fixtures for testing.
"""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app):
    """Create database for testing."""
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth_client(client, db):
    """Create authenticated test client with reader user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16),
        role='reader',
        is_active=True,
        is_confirmed=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'csrf_token': 'test'  # CSRF disabled in testing
    })
    
    return client


@pytest.fixture(scope='function')
def admin_client(client, db):
    """Create authenticated test client with admin user."""
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin123', method='pbkdf2:sha256', salt_length=16),
        role='admin',
        is_active=True,
        is_confirmed=True
    )
    db.session.add(admin)
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'email': 'admin@example.com',
        'password': 'admin123',
        'csrf_token': 'test'
    })
    
    return client


@pytest.fixture(scope='function')
def editor_client(client, db):
    """Create authenticated test client with editor user."""
    editor = User(
        username='editor',
        email='editor@example.com',
        password_hash=generate_password_hash('editor123', method='pbkdf2:sha256', salt_length=16),
        role='editor',
        is_active=True,
        is_confirmed=True
    )
    db.session.add(editor)
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'email': 'editor@example.com',
        'password': 'editor123',
        'csrf_token': 'test'
    })
    
    return client
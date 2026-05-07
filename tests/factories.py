"""
Factory Boy factories for creating test data.
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from werkzeug.security import generate_password_hash
from slugify import slugify
from datetime import datetime, timedelta
import random

from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like


fake = Faker()


class UserFactory(SQLAlchemyModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    username = factory.LazyAttribute(lambda x: fake.user_name())
    email = factory.LazyAttribute(lambda x: fake.email())
    password_hash = factory.LazyAttribute(
        lambda x: generate_password_hash('password123', method='pbkdf2:sha256', salt_length=16)
    )
    role = 'reader'
    is_active = True
    is_confirmed = True
    confirmed_at = factory.LazyFunction(datetime.utcnow)
    bio = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=200))


class CategoryFactory(SQLAlchemyModelFactory):
    """Factory for creating Category instances."""
    
    class Meta:
        model = Category
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = factory.LazyAttribute(lambda x: fake.word().capitalize())
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = factory.LazyAttribute(lambda x: fake.sentence())
    color = factory.LazyAttribute(lambda x: fake.hex_color())


class TagFactory(SQLAlchemyModelFactory):
    """Factory for creating Tag instances."""
    
    class Meta:
        model = Tag
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    name = factory.LazyAttribute(lambda x: fake.word().capitalize())
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))


class PostFactory(SQLAlchemyModelFactory):
    """Factory for creating Post instances."""
    
    class Meta:
        model = Post
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=6).rstrip('.'))
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    body = factory.LazyAttribute(
        lambda x: '<p>' + '</p><p>'.join([fake.paragraph() for _ in range(3)]) + '</p>'
    )
    excerpt = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=200))
    status = 'published'
    views = factory.LazyAttribute(lambda x: random.randint(10, 1000))
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    published_at = factory.LazyFunction(
        lambda: datetime.utcnow() - timedelta(days=random.randint(0, 30))
    )
    created_at = factory.LazyAttribute(
        lambda obj: obj.published_at - timedelta(hours=random.randint(1, 24))
    )


class CommentFactory(SQLAlchemyModelFactory):
    """Factory for creating Comment instances."""
    
    class Meta:
        model = Comment
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    body = factory.LazyAttribute(lambda x: fake.paragraph(nb_sentences=3))
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    is_approved = True
    created_at = factory.LazyFunction(datetime.utcnow)


class LikeFactory(SQLAlchemyModelFactory):
    """Factory for creating Like instances."""
    
    class Meta:
        model = Like
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
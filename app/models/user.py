import uuid
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import String, Text, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class User(UserMixin, db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum('reader', 'editor', 'admin', name='user_role'), 
        default='reader', 
        nullable=False
    )
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confirmed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", lazy='dynamic')
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author", lazy='dynamic')
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user", lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        """Return user ID as string for Flask-Login."""
        return str(self.id)
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    @property
    def is_editor(self):
        """Check if user is editor or admin."""
        return self.role in ('editor', 'admin')
    
    def can_edit_post(self, post):
        """Check if user can edit a specific post."""
        return self.is_admin or (self.is_editor and post.author_id == self.id)
    
    def get_avatar_url(self, size=80):
        """Get user avatar URL with fallback to Gravatar."""
        if self.avatar_url:
            return self.avatar_url
        
        import hashlib
        email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{email_hash}?d=identicon&s={size}'
    
    def to_dict(self, include_email=False):
        """Convert user to dictionary for API responses."""
        data = {
            'id': str(self.id),
            'username': self.username,
            'role': self.role,
            'avatar_url': self.get_avatar_url(),
            'bio': self.bio,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
        
        if include_email:
            data['email'] = self.email
            data['is_confirmed'] = self.is_confirmed
        
        return data
import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Category(db.Model):
    """Category model for organizing posts."""
    
    __tablename__ = 'categories'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(110), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default='#6366f1', nullable=False)  # hex color
    
    # Relationships
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category", lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @property
    def post_count(self):
        """Get count of published posts in this category."""
        return self.posts.filter_by(status='published').count()
    
    def to_dict(self):
        """Convert category to dictionary for API responses."""
        return {
            'id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color': self.color,
            'post_count': self.post_count
        }
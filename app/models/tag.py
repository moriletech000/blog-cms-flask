import uuid
from sqlalchemy import String, Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


# Association table for many-to-many relationship between posts and tags
post_tags = Table(
    'post_tags',
    db.Model.metadata,
    Column('post_id', UUID(as_uuid=True), ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)
)


class Tag(db.Model):
    """Tag model for labeling posts."""
    
    __tablename__ = 'tags'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    
    # Relationships
    posts: Mapped[list["Post"]] = relationship(
        "Post", 
        secondary=post_tags, 
        back_populates="tags",
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    @property
    def post_count(self):
        """Get count of published posts with this tag."""
        return self.posts.filter_by(status='published').count()
    
    def to_dict(self):
        """Convert tag to dictionary for API responses."""
        return {
            'id': str(self.id),
            'name': self.name,
            'slug': self.slug,
            'post_count': self.post_count
        }
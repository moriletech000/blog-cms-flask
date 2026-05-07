import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, Enum, ForeignKey, event
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db
from app.models.tag import post_tags


class Post(db.Model):
    """Post model for blog articles."""
    
    __tablename__ = 'posts'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str] = mapped_column(String(500), nullable=True)
    cover_image: Mapped[str] = mapped_column(String(255), nullable=True)
    cover_webp: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum('draft', 'published', 'archived', name='post_status'), 
        default='draft', 
        nullable=False
    )
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reading_time: Mapped[int] = mapped_column(Integer, nullable=True)  # minutes
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    search_vector: Mapped[str] = mapped_column(TSVECTOR, nullable=True)
    
    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="posts")
    category: Mapped["Category"] = relationship("Category", back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", 
        secondary=post_tags, 
        back_populates="posts",
        lazy='dynamic'
    )
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", lazy='dynamic')
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post", lazy='dynamic')
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    @property
    def like_count(self):
        """Get count of likes for this post."""
        return self.likes.count()
    
    @property
    def comment_count(self):
        """Get count of approved comments for this post."""
        return self.comments.filter_by(is_approved=True).count()
    
    @property
    def is_published(self):
        """Check if post is published."""
        return self.status == 'published'
    
    def get_cover_image_url(self):
        """Get cover image URL with fallback."""
        if self.cover_webp:
            return f'/static/uploads/{self.cover_webp}'
        elif self.cover_image:
            return f'/static/uploads/{self.cover_image}'
        return None
    
    def get_excerpt(self, length=160):
        """Get post excerpt, auto-generated if not set."""
        if self.excerpt:
            return self.excerpt
        
        # Strip HTML tags and get first N characters
        import re
        clean_body = re.sub(r'<[^>]+>', '', self.body)
        if len(clean_body) <= length:
            return clean_body
        return clean_body[:length].rsplit(' ', 1)[0] + '...'
    
    def calculate_reading_time(self):
        """Calculate reading time based on word count."""
        import re
        # Strip HTML tags and count words
        clean_body = re.sub(r'<[^>]+>', '', self.body)
        word_count = len(clean_body.split())
        # Average reading speed: 200 words per minute
        return max(1, round(word_count / 200))
    
    def to_dict(self, include_body=False):
        """Convert post to dictionary for API responses."""
        data = {
            'id': str(self.id),
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.get_excerpt(),
            'cover_image': self.get_cover_image_url(),
            'status': self.status,
            'views': self.views,
            'reading_time': self.reading_time,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'author': self.author.to_dict() if self.author else None,
            'category': self.category.to_dict() if self.category else None,
            'tags': [tag.to_dict() for tag in self.tags],
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_body:
            data['body'] = self.body
        
        return data


# Event listeners for automatic field updates
@event.listens_for(Post, 'before_insert')
@event.listens_for(Post, 'before_update')
def update_post_fields(mapper, connection, target):
    """Auto-update slug, excerpt, and reading time before save."""
    from slugify import slugify
    
    # Generate slug from title
    if target.title:
        base_slug = slugify(target.title)
        target.slug = base_slug
        
        # Ensure slug uniqueness (simple approach for this example)
        # In production, you might want more sophisticated slug generation
        
    # Auto-generate excerpt if not provided
    if not target.excerpt and target.body:
        target.excerpt = target.get_excerpt()
    
    # Calculate reading time
    if target.body:
        target.reading_time = target.calculate_reading_time()


@event.listens_for(Post, 'after_insert')
@event.listens_for(Post, 'after_update')
def process_cover_image(mapper, connection, target):
    """Trigger image processing task after post save."""
    if target.cover_image:
        from app.tasks.images import process_cover_image
        process_cover_image.delay(str(target.id))
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


class Comment(db.Model):
    """Comment model for post discussions."""
    
    __tablename__ = 'comments'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('posts.id'), nullable=False)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('comments.id'), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    parent: Mapped["Comment"] = relationship("Comment", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f'<Comment by {self.author.username if self.author else "Unknown"}>'
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent_id is not None
    
    def get_replies(self):
        """Get approved replies to this comment."""
        return Comment.query.filter_by(
            parent_id=self.id, 
            is_approved=True
        ).order_by(Comment.created_at.asc()).all()
    
    def time_ago(self):
        """Get human-readable time since comment was created."""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        created = self.created_at.replace(tzinfo=timezone.utc)
        diff = now - created
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    def to_dict(self):
        """Convert comment to dictionary for API responses."""
        return {
            'id': str(self.id),
            'body': self.body,
            'author': self.author.to_dict() if self.author else None,
            'post_id': str(self.post_id),
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'is_approved': self.is_approved,
            'is_reply': self.is_reply,
            'created_at': self.created_at.isoformat(),
            'time_ago': self.time_ago()
        }
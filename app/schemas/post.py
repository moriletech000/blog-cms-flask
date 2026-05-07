from marshmallow import Schema, fields, validate
from app.schemas.user import UserPublicSchema
from app.schemas.comment import CommentSchema


class CategorySchema(Schema):
    """Category schema."""
    
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    slug = fields.Str(dump_only=True)
    description = fields.Str(allow_none=True, validate=validate.Length(max=255))
    color = fields.Str(validate=validate.Length(min=7, max=7))
    post_count = fields.Int(dump_only=True)


class TagSchema(Schema):
    """Tag schema."""
    
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    slug = fields.Str(dump_only=True)
    post_count = fields.Int(dump_only=True)


class PostSchema(Schema):
    """Full post schema."""
    
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    slug = fields.Str(dump_only=True)
    body = fields.Str(required=True)
    excerpt = fields.Str(allow_none=True, validate=validate.Length(max=500))
    cover_image = fields.Str(dump_only=True, allow_none=True)
    status = fields.Str(validate=validate.OneOf(['draft', 'published', 'archived']))
    views = fields.Int(dump_only=True)
    reading_time = fields.Int(dump_only=True, allow_none=True)
    like_count = fields.Int(dump_only=True)
    comment_count = fields.Int(dump_only=True)
    author = fields.Nested(UserPublicSchema, dump_only=True)
    category = fields.Nested(CategorySchema, dump_only=True, allow_none=True)
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    published_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PostListSchema(Schema):
    """Simplified post schema for list views."""
    
    id = fields.Str(dump_only=True)
    title = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
    excerpt = fields.Str(dump_only=True)
    cover_image = fields.Str(dump_only=True, allow_none=True)
    status = fields.Str(dump_only=True)
    views = fields.Int(dump_only=True)
    reading_time = fields.Int(dump_only=True, allow_none=True)
    like_count = fields.Int(dump_only=True)
    comment_count = fields.Int(dump_only=True)
    author = fields.Nested(UserPublicSchema, dump_only=True)
    category = fields.Nested(CategorySchema, dump_only=True, allow_none=True)
    tags = fields.List(fields.Nested(TagSchema), dump_only=True)
    published_at = fields.DateTime(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)


class PostCreateSchema(Schema):
    """Schema for creating posts."""
    
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    body = fields.Str(required=True)
    excerpt = fields.Str(allow_none=True, validate=validate.Length(max=500))
    status = fields.Str(validate=validate.OneOf(['draft', 'published']), missing='draft')
    category_id = fields.Str(allow_none=True)
    tags = fields.List(fields.Str(), missing=[])


class PostUpdateSchema(Schema):
    """Schema for updating posts."""
    
    title = fields.Str(validate=validate.Length(min=1, max=200))
    body = fields.Str()
    excerpt = fields.Str(allow_none=True, validate=validate.Length(max=500))
    status = fields.Str(validate=validate.OneOf(['draft', 'published', 'archived']))
    category_id = fields.Str(allow_none=True)
    tags = fields.List(fields.Str())


class PaginationSchema(Schema):
    """Pagination metadata schema."""
    
    page = fields.Int(required=True)
    per_page = fields.Int(required=True)
    total = fields.Int(required=True)
    pages = fields.Int(required=True)
    has_prev = fields.Bool(required=True)
    has_next = fields.Bool(required=True)
    prev_num = fields.Int(allow_none=True)
    next_num = fields.Int(allow_none=True)


class PostListResponseSchema(Schema):
    """Schema for paginated post list responses."""
    
    data = fields.List(fields.Nested(PostListSchema), required=True)
    meta = fields.Nested(PaginationSchema, required=True)
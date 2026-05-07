from marshmallow import Schema, fields, validate
from app.schemas.user import UserPublicSchema


class CommentSchema(Schema):
    """Comment schema."""
    
    id = fields.Str(dump_only=True)
    body = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    author = fields.Nested(UserPublicSchema, dump_only=True)
    post_id = fields.Str(dump_only=True)
    parent_id = fields.Str(dump_only=True, allow_none=True)
    is_approved = fields.Bool(dump_only=True)
    is_reply = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    time_ago = fields.Str(dump_only=True)


class CommentCreateSchema(Schema):
    """Schema for creating comments."""
    
    body = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    parent_id = fields.Str(allow_none=True)


class CommentUpdateSchema(Schema):
    """Schema for updating comments."""
    
    body = fields.Str(validate=validate.Length(min=1, max=2000))
    is_approved = fields.Bool()


class CommentListResponseSchema(Schema):
    """Schema for paginated comment list responses."""
    
    data = fields.List(fields.Nested(CommentSchema), required=True)
    meta = fields.Nested('PaginationSchema', required=True)
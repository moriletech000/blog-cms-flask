from marshmallow import Schema, fields, validate


class UserPublicSchema(Schema):
    """Public user schema for API responses."""
    
    id = fields.Str(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    role = fields.Str(dump_only=True)
    avatar_url = fields.Str(allow_none=True)
    bio = fields.Str(allow_none=True, validate=validate.Length(max=500))
    created_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(dump_only=True)


class UserSchema(UserPublicSchema):
    """Full user schema including private fields."""
    
    email = fields.Email(required=True)
    is_confirmed = fields.Bool(dump_only=True)
    confirmed_at = fields.DateTime(dump_only=True, allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """Schema for user creation."""
    
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    bio = fields.Str(allow_none=True, validate=validate.Length(max=500))


class UserUpdateSchema(Schema):
    """Schema for user updates."""
    
    username = fields.Str(validate=validate.Length(min=3, max=20))
    email = fields.Email()
    bio = fields.Str(allow_none=True, validate=validate.Length(max=500))
    avatar_url = fields.Str(allow_none=True, validate=validate.Length(max=255))


class LoginSchema(Schema):
    """Schema for user login."""
    
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    remember_me = fields.Bool(missing=False)


class TokenSchema(Schema):
    """Schema for JWT token response."""
    
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)
    token_type = fields.Str(missing='Bearer')
    expires_in = fields.Int(required=True)


class RefreshTokenSchema(Schema):
    """Schema for token refresh."""
    
    refresh_token = fields.Str(required=True)
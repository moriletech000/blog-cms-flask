import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_restx import Resource, Namespace, fields
from flask_login import current_user
from werkzeug.security import check_password_hash
from marshmallow import ValidationError
from app.blueprints.api import api
from app.models.user import User
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.extensions import db, limiter
from app.schemas.user import LoginSchema, TokenSchema, RefreshTokenSchema
from app.schemas.post import PostListResponseSchema, PostSchema, PostCreateSchema, PostUpdateSchema
from app.schemas.comment import CommentSchema, CommentCreateSchema, CommentListResponseSchema
from app.utils.helpers import paginate_query


# JWT helper functions
def generate_tokens(user):
    """Generate access and refresh tokens for user."""
    access_payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    refresh_payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + current_app.config['JWT_REFRESH_TOKEN_EXPIRES'],
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    access_token = jwt.encode(access_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
    }


def verify_jwt_token(token, token_type='access'):
    """Verify JWT token and return user."""
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        
        if payload.get('type') != token_type:
            return None
        
        user = User.query.get(payload['user_id'])
        if user and user.is_active:
            return user
        
        return None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def jwt_required(f):
    """Decorator to require valid JWT token."""
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return {'error': 'Invalid authorization header format'}, 401
        
        if not token:
            return {'error': 'Authorization token required'}, 401
        
        user = verify_jwt_token(token)
        if not user:
            return {'error': 'Invalid or expired token'}, 401
        
        # Set current user for the request
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated


def editor_required(f):
    """Decorator to require editor or admin role."""
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return {'error': 'Authentication required'}, 401
        
        if not request.current_user.is_editor:
            return {'error': 'Editor privileges required'}, 403
        
        return f(*args, **kwargs)
    
    return decorated


# API Namespaces
auth_ns = Namespace('auth', description='Authentication operations')
posts_ns = Namespace('posts', description='Post operations')
categories_ns = Namespace('categories', description='Category operations')
tags_ns = Namespace('tags', description='Tag operations')
users_ns = Namespace('users', description='User operations')

api.add_namespace(auth_ns)
api.add_namespace(posts_ns)
api.add_namespace(categories_ns)
api.add_namespace(tags_ns)
api.add_namespace(users_ns)


# Auth endpoints
@auth_ns.route('/token')
class AuthToken(Resource):
    @limiter.limit("10 per minute")
    def post(self):
        """Login and get JWT tokens."""
        try:
            schema = LoginSchema()
            data = schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Validation error', 'messages': err.messages}, 400
        
        user = User.query.filter_by(email=data['email'].lower()).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return {'error': 'Invalid credentials'}, 401
        
        if not user.is_active:
            return {'error': 'Account deactivated'}, 401
        
        tokens = generate_tokens(user)
        return TokenSchema().dump(tokens)


@auth_ns.route('/refresh')
class AuthRefresh(Resource):
    def post(self):
        """Refresh access token."""
        try:
            schema = RefreshTokenSchema()
            data = schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Validation error', 'messages': err.messages}, 400
        
        user = verify_jwt_token(data['refresh_token'], token_type='refresh')
        if not user:
            return {'error': 'Invalid refresh token'}, 401
        
        tokens = generate_tokens(user)
        return TokenSchema().dump(tokens)


# Posts endpoints
@posts_ns.route('')
class PostList(Resource):
    @limiter.limit("100 per minute")
    def get(self):
        """Get paginated list of published posts."""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)
        category = request.args.get('category')
        tag = request.args.get('tag')
        search = request.args.get('q')
        
        query = Post.query.filter_by(status='published')
        
        # Apply filters
        if category:
            query = query.join(Category).filter(Category.slug == category)
        
        if tag:
            query = query.join(Post.tags).filter(Tag.slug == tag)
        
        if search:
            query = query.filter(Post.title.contains(search))
        
        query = query.order_by(Post.published_at.desc())
        
        result = paginate_query(query, page, per_page)
        
        # Serialize posts
        from app.schemas.post import PostListSchema
        posts_schema = PostListSchema(many=True)
        
        return {
            'data': posts_schema.dump(result['items']),
            'meta': result['meta']
        }
    
    @jwt_required
    @editor_required
    def post(self):
        """Create new post."""
        try:
            schema = PostCreateSchema()
            data = schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Validation error', 'messages': err.messages}, 400
        
        from slugify import slugify
        
        post = Post(
            title=data['title'],
            slug=slugify(data['title']),
            body=data['body'],
            excerpt=data.get('excerpt'),
            status=data.get('status', 'draft'),
            author_id=request.current_user.id,
            category_id=data.get('category_id')
        )
        
        if data.get('status') == 'published':
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.flush()
        
        # Handle tags
        if data.get('tags'):
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, slug=slugify(tag_name))
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.commit()
        
        return PostSchema().dump(post), 201


@posts_ns.route('/<string:slug>')
class PostDetail(Resource):
    def get(self, slug):
        """Get post by slug."""
        post = Post.query.filter_by(slug=slug, status='published').first()
        if not post:
            return {'error': 'Post not found'}, 404
        
        return PostSchema().dump(post)
    
    @jwt_required
    def put(self, slug):
        """Update post."""
        post = Post.query.filter_by(slug=slug).first()
        if not post:
            return {'error': 'Post not found'}, 404
        
        # Check permissions
        if not request.current_user.can_edit_post(post):
            return {'error': 'Permission denied'}, 403
        
        try:
            schema = PostUpdateSchema()
            data = schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Validation error', 'messages': err.messages}, 400
        
        # Update fields
        if 'title' in data:
            from slugify import slugify
            post.title = data['title']
            post.slug = slugify(data['title'])
        
        if 'body' in data:
            post.body = data['body']
        
        if 'excerpt' in data:
            post.excerpt = data['excerpt']
        
        if 'status' in data:
            old_status = post.status
            post.status = data['status']
            
            # Set published_at if changing to published
            if old_status != 'published' and data['status'] == 'published':
                post.published_at = datetime.utcnow()
        
        if 'category_id' in data:
            post.category_id = data['category_id']
        
        # Handle tags
        if 'tags' in data:
            post.tags.clear()
            for tag_name in data['tags']:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    from slugify import slugify
                    tag = Tag(name=tag_name, slug=slugify(tag_name))
                    db.session.add(tag)
                post.tags.append(tag)
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return PostSchema().dump(post)
    
    @jwt_required
    def delete(self, slug):
        """Archive post."""
        post = Post.query.filter_by(slug=slug).first()
        if not post:
            return {'error': 'Post not found'}, 404
        
        # Check permissions
        if not request.current_user.can_edit_post(post):
            return {'error': 'Permission denied'}, 403
        
        post.status = 'archived'
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Post archived successfully'}


@posts_ns.route('/<string:slug>/comments')
class PostComments(Resource):
    def get(self, slug):
        """Get comments for a post."""
        post = Post.query.filter_by(slug=slug, status='published').first()
        if not post:
            return {'error': 'Post not found'}, 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 50)
        
        query = Comment.query.filter_by(
            post_id=post.id,
            parent_id=None,
            is_approved=True
        ).order_by(Comment.created_at.asc())
        
        result = paginate_query(query, page, per_page)
        
        return {
            'data': CommentSchema(many=True).dump(result['items']),
            'meta': result['meta']
        }
    
    @jwt_required
    def post(self, slug):
        """Add comment to post."""
        post = Post.query.filter_by(slug=slug, status='published').first()
        if not post:
            return {'error': 'Post not found'}, 404
        
        if not request.current_user.is_confirmed:
            return {'error': 'Email confirmation required'}, 403
        
        try:
            schema = CommentCreateSchema()
            data = schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Validation error', 'messages': err.messages}, 400
        
        comment = Comment(
            body=data['body'],
            author_id=request.current_user.id,
            post_id=post.id,
            parent_id=data.get('parent_id')
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Send notification
        if post.author_id != request.current_user.id:
            from app.tasks.email import send_comment_notification
            send_comment_notification.delay(str(comment.id))
        
        return CommentSchema().dump(comment), 201


# Categories endpoint
@categories_ns.route('')
class CategoryList(Resource):
    def get(self):
        """Get all categories."""
        categories = Category.query.order_by(Category.name).all()
        from app.schemas.post import CategorySchema
        return CategorySchema(many=True).dump(categories)


# Tags endpoint
@tags_ns.route('')
class TagList(Resource):
    def get(self):
        """Get all tags with post counts."""
        tags = Tag.query.order_by(Tag.name).all()
        from app.schemas.post import TagSchema
        return TagSchema(many=True).dump(tags)


# Users endpoints
@users_ns.route('/me')
class UserProfile(Resource):
    @jwt_required
    def get(self):
        """Get current user profile."""
        from app.schemas.user import UserSchema
        return UserSchema().dump(request.current_user)
    
    @jwt_required
    def put(self):
        """Update current user profile."""
        try:
            from app.schemas.user import UserUpdateSchema
            schema = UserUpdateSchema()
            data = schema.load(request.json)
        except ValidationError as err:
            return {'error': 'Validation error', 'messages': err.messages}, 400
        
        user = request.current_user
        
        # Update fields
        if 'username' in data:
            # Check if username is taken
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user.id:
                return {'error': 'Username already taken'}, 400
            user.username = data['username']
        
        if 'email' in data:
            # Check if email is taken
            existing = User.query.filter_by(email=data['email'].lower()).first()
            if existing and existing.id != user.id:
                return {'error': 'Email already registered'}, 400
            user.email = data['email'].lower()
        
        if 'bio' in data:
            user.bio = data['bio']
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        from app.schemas.user import UserSchema
        return UserSchema().dump(user)


@users_ns.route('/<string:username>')
class UserPublicProfile(Resource):
    def get(self, username):
        """Get public user profile and their posts."""
        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            return {'error': 'User not found'}, 404
        
        # Get user's published posts
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 20)
        
        posts_query = Post.query.filter_by(
            author_id=user.id,
            status='published'
        ).order_by(Post.published_at.desc())
        
        posts_result = paginate_query(posts_query, page, per_page)
        
        from app.schemas.user import UserPublicSchema
        from app.schemas.post import PostListSchema
        
        return {
            'user': UserPublicSchema().dump(user),
            'posts': {
                'data': PostListSchema(many=True).dump(posts_result['items']),
                'meta': posts_result['meta']
            }
        }
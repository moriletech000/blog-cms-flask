from flask import render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, func, text
from datetime import datetime, timedelta
from app.blueprints.blog import blog_bp
from app.blueprints.blog.forms import CommentForm, SearchForm
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.like import Like
from app.extensions import db, cache, redis_client
from app.tasks.email import send_comment_notification


@blog_bp.route('/')
@cache.cached(timeout=300, key_prefix='index_page_%s')
def index():
    """Blog homepage with paginated posts."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get published posts
    posts = Post.query.filter_by(status='published').order_by(
        desc(Post.published_at)
    ).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Get featured post (most viewed this week)
    week_ago = datetime.utcnow() - timedelta(days=7)
    featured_post = Post.query.filter(
        Post.status == 'published',
        Post.published_at >= week_ago
    ).order_by(desc(Post.views)).first()
    
    # Sidebar data
    recent_posts = Post.query.filter_by(status='published').order_by(
        desc(Post.published_at)
    ).limit(5).all()
    
    popular_tags = db.session.query(
        Tag, func.count(Post.id).label('post_count')
    ).join(
        Post.tags
    ).filter(
        Post.status == 'published'
    ).group_by(Tag.id).order_by(
        desc('post_count')
    ).limit(10).all()
    
    categories_with_counts = db.session.query(
        Category, func.count(Post.id).label('post_count')
    ).outerjoin(Post).filter(
        (Post.status == 'published') | (Post.id.is_(None))
    ).group_by(Category.id).all()
    
    return render_template(
        'blog/index.html',
        posts=posts,
        featured_post=featured_post,
        recent_posts=recent_posts,
        popular_tags=popular_tags,
        categories=categories_with_counts
    )


@blog_bp.route('/post/<slug>')
def post_detail(slug):
    """Individual post view."""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Increment view counter in Redis
    redis_key = f'post:views:{post.id}'
    redis_client.incr(redis_key)
    
    # Get comments (top-level only, replies loaded separately)
    comments = Comment.query.filter_by(
        post_id=post.id, 
        parent_id=None, 
        is_approved=True
    ).order_by(Comment.created_at.asc()).all()
    
    # Get related posts (same category or tags)
    related_posts = Post.query.filter(
        Post.id != post.id,
        Post.status == 'published'
    ).filter(
        (Post.category_id == post.category_id) |
        (Post.tags.any(Tag.id.in_([tag.id for tag in post.tags])))
    ).order_by(desc(Post.published_at)).limit(3).all()
    
    # Check if current user liked this post
    user_liked = False
    if current_user.is_authenticated:
        user_liked = Like.query.filter_by(
            user_id=current_user.id, 
            post_id=post.id
        ).first() is not None
    
    # Comment form
    form = CommentForm()
    
    return render_template(
        'blog/post.html',
        post=post,
        comments=comments,
        related_posts=related_posts,
        user_liked=user_liked,
        form=form
    )


@blog_bp.route('/post/<slug>/like', methods=['POST'])
@login_required
def toggle_like(slug):
    """Toggle like on a post (AJAX endpoint)."""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    existing_like = Like.query.filter_by(
        user_id=current_user.id, 
        post_id=post.id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        liked = False
    else:
        # Like
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        liked = True
    
    db.session.commit()
    
    # Get updated like count
    like_count = Like.query.filter_by(post_id=post.id).count()
    
    return jsonify({
        'liked': liked,
        'count': like_count
    })


@blog_bp.route('/post/<slug>/comment', methods=['POST'])
@login_required
def add_comment(slug):
    """Add comment to a post."""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Check if user is confirmed
    if not current_user.is_confirmed:
        flash('Please confirm your email address before commenting.', 'warning')
        return redirect(url_for('blog.post_detail', slug=slug))
    
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            author_id=current_user.id,
            post_id=post.id,
            parent_id=form.parent_id.data if form.parent_id.data else None
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Send notification to post author (if not commenting on own post)
        if post.author_id != current_user.id:
            send_comment_notification.delay(str(comment.id))
        
        flash('Comment posted successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('blog.post_detail', slug=slug))


@blog_bp.route('/category/<slug>')
def category_posts(slug):
    """Posts filtered by category."""
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(
        category_id=category.id, 
        status='published'
    ).order_by(desc(Post.published_at)).paginate(
        page=page, 
        per_page=10, 
        error_out=False
    )
    
    return render_template(
        'blog/category.html',
        category=category,
        posts=posts
    )


@blog_bp.route('/tag/<slug>')
def tag_posts(slug):
    """Posts filtered by tag."""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter(
        Post.tags.contains(tag),
        Post.status == 'published'
    ).order_by(desc(Post.published_at)).paginate(
        page=page, 
        per_page=10, 
        error_out=False
    )
    
    return render_template(
        'blog/tag.html',
        tag=tag,
        posts=posts
    )


@blog_bp.route('/search')
def search():
    """Full-text search for posts."""
    form = SearchForm()
    posts = None
    query_time = 0
    
    if request.args.get('q'):
        form.q.data = request.args.get('q')
        search_term = request.args.get('q').strip()
        page = request.args.get('page', 1, type=int)
        
        if search_term:
            # Record start time for query performance
            start_time = datetime.utcnow()
            
            # PostgreSQL full-text search
            search_query = func.plainto_tsquery('english', search_term)
            posts = Post.query.filter(
                Post.status == 'published',
                Post.search_vector.op('@@')(search_query)
            ).order_by(
                func.ts_rank(Post.search_vector, search_query).desc(),
                desc(Post.published_at)
            ).paginate(
                page=page, 
                per_page=10, 
                error_out=False
            )
            
            # Calculate query time
            end_time = datetime.utcnow()
            query_time = (end_time - start_time).total_seconds()
    
    return render_template(
        'blog/search.html',
        form=form,
        posts=posts,
        query_time=query_time,
        search_term=request.args.get('q', '')
    )
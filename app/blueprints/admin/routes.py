import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func, extract
from werkzeug.utils import secure_filename
from slugify import slugify
from app.blueprints.admin import admin_bp
from app.blueprints.admin.forms import PostForm, CategoryForm, UserEditForm
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.models.comment import Comment
from app.models.like import Like
from app.extensions import db, cache, redis_client
from app.utils.decorators import admin_required
from app.utils.upload import save_image, delete_image


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    
    # Post statistics
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status='published').count()
    draft_posts = Post.query.filter_by(status='draft').count()
    archived_posts = Post.query.filter_by(status='archived').count()
    
    # User statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(role='admin').count()
    editor_users = User.query.filter_by(role='editor').count()
    reader_users = User.query.filter_by(role='reader').count()
    
    # Comment statistics
    total_comments = Comment.query.count()
    approved_comments = Comment.query.filter_by(is_approved=True).count()
    pending_comments = Comment.query.filter_by(is_approved=False).count()
    
    # Likes today (from Redis)
    today = datetime.utcnow().date()
    likes_today = 0
    try:
        # Get all like keys from Redis and count today's likes
        like_keys = redis_client.keys('post:views:*')
        # This is a simplified approach - in production you'd want better tracking
        likes_today = len(like_keys)  # Placeholder
    except:
        likes_today = 0
    
    # Recent activity
    recent_posts = Post.query.order_by(desc(Post.created_at)).limit(5).all()
    recent_comments = Comment.query.order_by(desc(Comment.created_at)).limit(5).all()
    
    # Posts published per month (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_posts = db.session.query(
        extract('year', Post.published_at).label('year'),
        extract('month', Post.published_at).label('month'),
        func.count(Post.id).label('count')
    ).filter(
        Post.status == 'published',
        Post.published_at >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    # Format for chart
    chart_data = []
    for year, month, count in monthly_posts:
        chart_data.append({
            'month': f"{int(year)}-{int(month):02d}",
            'count': count
        })
    
    return render_template(
        'admin/dashboard.html',
        stats={
            'posts': {
                'total': total_posts,
                'published': published_posts,
                'draft': draft_posts,
                'archived': archived_posts
            },
            'users': {
                'total': total_users,
                'admin': admin_users,
                'editor': editor_users,
                'reader': reader_users
            },
            'comments': {
                'total': total_comments,
                'approved': approved_comments,
                'pending': pending_comments
            },
            'likes_today': likes_today
        },
        recent_posts=recent_posts,
        recent_comments=recent_comments,
        chart_data=chart_data
    )


@admin_bp.route('/posts')
@login_required
@admin_required
def posts():
    """List all posts with filtering and search."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    query = Post.query
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(Post.title.contains(search_query))
    
    posts = query.order_by(desc(Post.created_at)).paginate(
        page=page, 
        per_page=20, 
        error_out=False
    )
    
    return render_template(
        'admin/posts.html',
        posts=posts,
        status_filter=status_filter,
        search_query=search_query
    )


@admin_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_post():
    """Create new post."""
    form = PostForm()
    
    if form.validate_on_submit():
        # Handle cover image upload
        cover_image_filename = None
        if form.cover_image.data:
            cover_image_filename = save_image(form.cover_image.data)
        
        # Create post
        post = Post(
            title=form.title.data,
            slug=slugify(form.title.data),
            body=form.body.data,
            excerpt=form.excerpt.data,
            cover_image=cover_image_filename,
            status=form.status.data,
            author_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data else None
        )
        
        # Set published_at if status is published
        if form.status.data == 'published':
            post.published_at = datetime.utcnow()
        
        db.session.add(post)
        db.session.flush()  # Get the post ID
        
        # Handle tags
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',') if name.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, slug=slugify(tag_name))
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.commit()
        
        # Clear cache
        cache.delete_memoized('index_page_1')
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin.edit_post', id=post.id))
    
    return render_template('admin/post_form.html', form=form, post=None)


@admin_bp.route('/posts/<uuid:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    """Edit existing post."""
    post = Post.query.get_or_404(id)
    
    # Check permissions (admin can edit all, editor can edit own)
    if not current_user.can_edit_post(post):
        flash('You do not have permission to edit this post.', 'error')
        return redirect(url_for('admin.posts'))
    
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        # Handle cover image upload
        if form.cover_image.data:
            # Delete old image
            if post.cover_image:
                delete_image(post.cover_image)
            if post.cover_webp:
                delete_image(post.cover_webp)
            
            # Save new image
            post.cover_image = save_image(form.cover_image.data)
            post.cover_webp = None  # Will be regenerated by Celery
        
        # Update post fields
        old_status = post.status
        post.title = form.title.data
        post.slug = slugify(form.title.data)
        post.body = form.body.data
        post.excerpt = form.excerpt.data
        post.status = form.status.data
        post.category_id = form.category_id.data if form.category_id.data else None
        post.updated_at = datetime.utcnow()
        
        # Set published_at if status changed to published
        if old_status != 'published' and form.status.data == 'published':
            post.published_at = datetime.utcnow()
        
        # Clear existing tags and add new ones
        post.tags.clear()
        if form.tags.data:
            tag_names = [name.strip() for name in form.tags.data.split(',') if name.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name, slug=slugify(tag_name))
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.commit()
        
        # Clear cache
        cache.delete_memoized('index_page_1')
        cache.delete_memoized(f'post_{post.slug}')
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin.edit_post', id=post.id))
    
    # Pre-populate tags field
    if post.tags:
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    return render_template('admin/post_form.html', form=form, post=post)


@admin_bp.route('/posts/<uuid:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_post(id):
    """Archive post (soft delete)."""
    post = Post.query.get_or_404(id)
    
    if not current_user.can_edit_post(post):
        flash('You do not have permission to delete this post.', 'error')
        return redirect(url_for('admin.posts'))
    
    post.status = 'archived'
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Clear cache
    cache.delete_memoized('index_page_1')
    cache.delete_memoized(f'post_{post.slug}')
    
    flash('Post archived successfully!', 'success')
    return redirect(url_for('admin.posts'))


@admin_bp.route('/posts/<uuid:id>/publish', methods=['POST'])
@login_required
@admin_required
def publish_post(id):
    """Publish a post."""
    post = Post.query.get_or_404(id)
    
    if not current_user.can_edit_post(post):
        flash('You do not have permission to publish this post.', 'error')
        return redirect(url_for('admin.posts'))
    
    post.status = 'published'
    post.published_at = datetime.utcnow()
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Clear cache
    cache.delete_memoized('index_page_1')
    
    flash('Post published successfully!', 'success')
    return redirect(url_for('admin.posts'))


@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """List and manage categories."""
    categories = Category.query.order_by(Category.name).all()
    form = CategoryForm()
    
    return render_template('admin/categories.html', categories=categories, form=form)


@admin_bp.route('/categories/new', methods=['POST'])
@login_required
@admin_required
def create_category():
    """Create new category."""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            slug=slugify(form.name.data),
            description=form.description.data,
            color=form.color.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/<uuid:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    """Delete category if no posts assigned."""
    category = Category.query.get_or_404(id)
    
    if category.posts.count() > 0:
        flash('Cannot delete category with assigned posts.', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('admin.categories'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List and manage users."""
    page = request.args.get('page', 1, type=int)
    
    users = User.query.order_by(desc(User.created_at)).paginate(
        page=page, 
        per_page=20, 
        error_out=False
    )
    
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<uuid:id>/role', methods=['POST'])
@login_required
@admin_required
def change_user_role(id):
    """Change user role."""
    user = User.query.get_or_404(id)
    new_role = request.form.get('role')
    
    if new_role in ['reader', 'editor', 'admin']:
        user.role = new_role
        user.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'User role updated to {new_role}.', 'success')
    else:
        flash('Invalid role specified.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<uuid:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(id):
    """Activate/deactivate user."""
    user = User.query.get_or_404(id)
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully.', 'success')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/comments')
@login_required
@admin_required
def comments():
    """Comment moderation."""
    page = request.args.get('page', 1, type=int)
    
    comments = Comment.query.order_by(desc(Comment.created_at)).paginate(
        page=page, 
        per_page=20, 
        error_out=False
    )
    
    return render_template('admin/comments.html', comments=comments)


@admin_bp.route('/comments/<uuid:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_comment_approval(id):
    """Approve/unapprove comment."""
    comment = Comment.query.get_or_404(id)
    
    comment.is_approved = not comment.is_approved
    db.session.commit()
    
    status = 'approved' if comment.is_approved else 'unapproved'
    flash(f'Comment {status} successfully.', 'success')
    
    return redirect(url_for('admin.comments'))
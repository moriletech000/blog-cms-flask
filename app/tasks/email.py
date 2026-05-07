from flask import current_app, render_template
from flask_mail import Message
from app.extensions import celery, mail, db
from app.models.user import User
from app.models.comment import Comment
from app.models.post import Post


@celery.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """Send welcome email with confirmation link."""
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"
        
        # Generate confirmation token
        from app.utils.helpers import generate_token
        token = generate_token(user.email, salt='email-confirm')
        
        # Create confirmation URL
        from flask import url_for
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        
        # Render email template
        html_body = render_template(
            'emails/welcome.html',
            user=user,
            confirm_url=confirm_url
        )
        
        text_body = f"""
        Welcome to our blog, {user.username}!
        
        Please confirm your email address by clicking the link below:
        {confirm_url}
        
        This link will expire in 1 hour.
        
        If you didn't create this account, please ignore this email.
        """
        
        # Send email
        msg = Message(
            subject='Welcome! Please confirm your email',
            recipients=[user.email],
            html=html_body,
            body=text_body
        )
        
        mail.send(msg)
        return f"Welcome email sent to {user.email}"
    
    except Exception as exc:
        current_app.logger.error(f"Error sending welcome email: {exc}")
        raise self.retry(countdown=60, exc=exc)


@celery.task(bind=True, max_retries=3)
def send_comment_notification(self, comment_id):
    """Send notification to post author when someone comments."""
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return f"Comment {comment_id} not found"
        
        post = comment.post
        if not post or not post.author:
            return f"Post or author not found for comment {comment_id}"
        
        # Don't send notification if author is commenting on their own post
        if comment.author_id == post.author_id:
            return "Author commented on own post, no notification sent"
        
        # Render email template
        html_body = render_template(
            'emails/comment_notification.html',
            post=post,
            comment=comment,
            post_url=url_for('blog.post_detail', slug=post.slug, _external=True)
        )
        
        text_body = f"""
        New comment on your post "{post.title}"
        
        {comment.author.username} wrote:
        {comment.body}
        
        View the full post and reply:
        {url_for('blog.post_detail', slug=post.slug, _external=True)}
        """
        
        # Send email
        msg = Message(
            subject=f'New comment on "{post.title}"',
            recipients=[post.author.email],
            html=html_body,
            body=text_body
        )
        
        mail.send(msg)
        return f"Comment notification sent to {post.author.email}"
    
    except Exception as exc:
        current_app.logger.error(f"Error sending comment notification: {exc}")
        raise self.retry(countdown=60, exc=exc)


@celery.task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id, token):
    """Send password reset email."""
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"
        
        # Create reset URL
        from flask import url_for
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        # Render email template
        html_body = render_template(
            'emails/password_reset.html',
            user=user,
            reset_url=reset_url
        )
        
        text_body = f"""
        Password Reset Request
        
        Hello {user.username},
        
        You requested a password reset for your account. Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 30 minutes.
        
        If you didn't request this reset, please ignore this email.
        """
        
        # Send email
        msg = Message(
            subject='Password Reset Request',
            recipients=[user.email],
            html=html_body,
            body=text_body
        )
        
        mail.send(msg)
        return f"Password reset email sent to {user.email}"
    
    except Exception as exc:
        current_app.logger.error(f"Error sending password reset email: {exc}")
        raise self.retry(countdown=60, exc=exc)


@celery.task(bind=True, max_retries=3)
def send_bulk_notification(self, subject, message, user_ids=None):
    """Send bulk notification to users."""
    try:
        if user_ids:
            users = User.query.filter(User.id.in_(user_ids)).all()
        else:
            users = User.query.filter_by(is_active=True).all()
        
        sent_count = 0
        for user in users:
            try:
                msg = Message(
                    subject=subject,
                    recipients=[user.email],
                    body=message
                )
                mail.send(msg)
                sent_count += 1
            except Exception as e:
                current_app.logger.error(f"Failed to send email to {user.email}: {e}")
        
        return f"Bulk notification sent to {sent_count} users"
    
    except Exception as exc:
        current_app.logger.error(f"Error sending bulk notification: {exc}")
        raise self.retry(countdown=60, exc=exc)
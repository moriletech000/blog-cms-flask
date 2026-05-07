from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import (
    RegistrationForm, LoginForm, ForgotPasswordForm, 
    ResetPasswordForm, ResendConfirmationForm, ProfileForm
)
from app.models.user import User
from app.extensions import db, limiter
from app.tasks.email import send_welcome_email, send_password_reset_email


def generate_token(email, salt='email-confirm'):
    """Generate a secure token for email confirmation or password reset."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=salt)


def verify_token(token, salt='email-confirm', expiration=3600):
    """Verify a token and return the email if valid."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            password_hash=generate_password_hash(
                form.password.data, 
                method='pbkdf2:sha256', 
                salt_length=16
            ),
            role='reader',
            is_active=True,
            is_confirmed=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email with confirmation link
        send_welcome_email.delay(str(user.id))
        
        flash('Registration successful! Please check your email to confirm your account.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or blog index
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('blog.index'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('blog.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """Forgot password form."""
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # Generate reset token
            token = generate_token(user.email, salt='password-reset')
            
            # Send reset email
            send_password_reset_email.delay(str(user.id), token)
        
        # Always show success message to prevent email enumeration
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    # Verify token (30 minutes expiration)
    email = verify_token(token, salt='password-reset', expiration=1800)
    if not email:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(
            form.password.data, 
            method='pbkdf2:sha256', 
            salt_length=16
        )
        db.session.commit()
        
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/confirm-email/<token>')
def confirm_email(token):
    """Confirm email address with token."""
    if current_user.is_authenticated and current_user.is_confirmed:
        return redirect(url_for('blog.index'))
    
    # Verify token (1 hour expiration)
    email = verify_token(token, salt='email-confirm', expiration=3600)
    if not email:
        flash('Invalid or expired confirmation link.', 'error')
        return redirect(url_for('auth.resend_confirmation'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid confirmation link.', 'error')
        return redirect(url_for('auth.register'))
    
    if user.is_confirmed:
        flash('Account already confirmed. Please log in.', 'info')
        return redirect(url_for('auth.login'))
    
    user.is_confirmed = True
    user.confirmed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Email confirmed successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-confirmation', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def resend_confirmation():
    """Resend email confirmation."""
    if current_user.is_authenticated and current_user.is_confirmed:
        return redirect(url_for('blog.index'))
    
    form = ResendConfirmationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and not user.is_confirmed:
            send_welcome_email.delay(str(user.id))
        
        flash('If an unconfirmed account with that email exists, a new confirmation link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resend_confirmation.html', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page."""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username is taken by another user
        if form.username.data != current_user.username:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('Username already taken.', 'error')
                return render_template('auth/profile.html', form=form)
        
        # Check if email is taken by another user
        if form.email.data.lower() != current_user.email:
            existing_user = User.query.filter_by(email=form.email.data.lower()).first()
            if existing_user:
                flash('Email already registered.', 'error')
                return render_template('auth/profile.html', form=form)
            
            # If email changed, require re-confirmation
            current_user.is_confirmed = False
            current_user.confirmed_at = None
            send_welcome_email.delay(str(current_user.id))
            flash('Email updated. Please check your new email to confirm your account.', 'info')
        
        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        current_user.bio = form.bio.data
        current_user.avatar_url = form.avatar_url.data
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form)
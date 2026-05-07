from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def editor_required(f):
    """Decorator to require editor or admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not current_user.is_editor:
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def confirmed_required(f):
    """Decorator to require confirmed email."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not current_user.is_confirmed:
            flash('Please confirm your email address to access this feature.', 'warning')
            return redirect(url_for('auth.resend_confirmation'))
        
        return f(*args, **kwargs)
    return decorated_function
import re
import secrets
from datetime import datetime, timezone
from flask import request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from slugify import slugify as python_slugify


def slugify(text):
    """Create URL-friendly slug from text."""
    return python_slugify(text, max_length=200)


def paginate_query(query, page=1, per_page=10):
    """Paginate a SQLAlchemy query and return pagination info."""
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'meta': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }
    }


def generate_token(data, salt='default', secret_key=None):
    """Generate a secure token for various purposes."""
    from flask import current_app
    
    if secret_key is None:
        secret_key = current_app.config['SECRET_KEY']
    
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(data, salt=salt)


def verify_token(token, salt='default', max_age=3600, secret_key=None):
    """Verify a token and return the data if valid."""
    from flask import current_app
    
    if secret_key is None:
        secret_key = current_app.config['SECRET_KEY']
    
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        data = serializer.loads(token, salt=salt, max_age=max_age)
        return data
    except (SignatureExpired, BadSignature):
        return None


def get_client_ip():
    """Get client IP address from request."""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']


def time_ago(dt):
    """Convert datetime to human-readable time ago string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


def strip_html_tags(text):
    """Remove HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def truncate_text(text, length=100, suffix='...'):
    """Truncate text to specified length."""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix


def generate_random_string(length=32):
    """Generate a random string for various purposes."""
    return secrets.token_urlsafe(length)


def is_safe_url(target):
    """Check if a URL is safe for redirects."""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def clean_filename(filename):
    """Clean filename for safe storage."""
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    
    return filename.strip('-')


def get_pagination_info(page, per_page, total):
    """Get pagination metadata."""
    pages = (total + per_page - 1) // per_page
    
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': pages,
        'has_prev': page > 1,
        'has_next': page < pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < pages else None
    }
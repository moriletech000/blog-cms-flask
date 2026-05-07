from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from celery import Celery
import redis


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)
cors = CORS()

# Redis connection
redis_client = None

# Celery instance
celery = Celery()


def init_extensions(app):
    """Initialize Flask extensions."""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Mail
    mail.init_app(app)
    
    # Cache
    cache.init_app(app)
    
    # Rate limiter
    limiter.init_app(app)
    
    # CORS - only for API routes
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Celery
    init_celery(app)


def init_celery(app):
    """Initialize Celery with Flask app context."""
    
    class FlaskTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        include=[
            'app.tasks.email',
            'app.tasks.images'
        ]
    )
    
    celery.Task = FlaskTask
    return celery


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    from app.models.user import User
    return User.query.get(user_id)
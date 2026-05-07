import os
import click
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from flask import Flask, render_template
from app.config import config
from app.extensions import init_extensions


def create_app(config_name=None):
    """Application factory pattern."""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize Sentry if DSN is provided
    if app.config.get('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration(),
                CeleryIntegration()
            ],
            traces_sample_rate=0.1,
            environment=config_name
        )
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Create upload directory
    upload_dir = os.path.join(app.instance_path, '..', app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_dir, exist_ok=True)
    
    return app


def register_blueprints(app):
    """Register application blueprints."""
    
    from app.blueprints.auth import auth_bp
    from app.blueprints.blog import blog_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api/v1')


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from app.extensions import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('errors/413.html'), 413


def register_context_processors(app):
    """Register context processors."""
    from app.context_processors import utility_processor
    app.context_processor(utility_processor)


def register_cli_commands(app):
    """Register CLI commands."""
    
    @app.cli.command()
    def seed_db():
        """Seed the database with initial data."""
        from app.models.user import User
        from app.extensions import db
        
        # Check if DB is already seeded
        if User.query.count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        from app.utils.seed import seed_database
        seed_database()
        print("Database seeded successfully!")
    
    @app.cli.command()
    @click.option('--email', required=True, help='Admin email')
    @click.option('--password', required=True, help='Admin password')
    def create_admin(email, password):
        """Create or promote user to admin role."""
        from app.models.user import User
        from app.extensions import db
        from werkzeug.security import generate_password_hash
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = 'admin'
            print(f"User {email} promoted to admin.")
        else:
            user = User(
                username=email.split('@')[0],
                email=email,
                password_hash=generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
                role='admin',
                is_active=True,
                is_confirmed=True
            )
            db.session.add(user)
            print(f"Admin user {email} created.")
        
        db.session.commit()
    
    @app.cli.command()
    def clear_cache():
        """Clear application cache."""
        from app.extensions import cache
        cache.clear()
        print("Cache cleared.")
    
    @app.cli.command()
    def run_migrations():
        """Run database migrations."""
        from flask_migrate import upgrade
        upgrade()
        print("Database migrations completed.")
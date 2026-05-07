#!/usr/bin/env python3
"""
Management script for the Flask application.
Provides CLI commands for database operations, user management, and maintenance tasks.
"""

import os
import click
from flask.cli import with_appcontext
from app import create_app
from app.extensions import db
from app.models.user import User


def create_cli_app():
    """Create Flask app for CLI commands."""
    return create_app(os.environ.get('FLASK_ENV', 'development'))


@click.command()
@with_appcontext
def seed_db():
    """Seed the database with initial data."""
    if User.query.count() > 0:
        click.echo("Database already contains data. Skipping seed.")
        return
    
    from app.utils.seed import seed_database
    seed_database()
    click.echo("Database seeded successfully!")


@click.command()
@click.option('--email', required=True, help='Admin email address')
@click.option('--password', required=True, help='Admin password')
@with_appcontext
def create_admin(email, password):
    """Create or promote user to admin role."""
    from werkzeug.security import generate_password_hash
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.role = 'admin'
        click.echo(f"User {email} promoted to admin.")
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
        click.echo(f"Admin user {email} created.")
    
    db.session.commit()


@click.command()
@with_appcontext
def clear_cache():
    """Clear application cache."""
    from app.extensions import cache
    cache.clear()
    click.echo("Cache cleared.")


@click.command()
@with_appcontext
def run_migrations():
    """Run database migrations."""
    from flask_migrate import upgrade
    upgrade()
    click.echo("Database migrations completed.")


@click.command()
@with_appcontext
def init_db():
    """Initialize database tables."""
    db.create_all()
    click.echo("Database tables created.")


@click.command()
@with_appcontext
def drop_db():
    """Drop all database tables."""
    if click.confirm('This will delete all data. Are you sure?'):
        db.drop_all()
        click.echo("Database tables dropped.")


@click.command()
@click.option('--count', default=10, help='Number of test posts to create')
@with_appcontext
def create_test_data(count):
    """Create test data for development."""
    from app.utils.seed import seed_database
    from faker import Faker
    from app.models.post import Post
    from app.models.user import User
    from app.models.category import Category
    from slugify import slugify
    from datetime import datetime, timedelta
    import random
    
    fake = Faker()
    
    # Get existing users and categories
    users = User.query.all()
    categories = Category.query.all()
    
    if not users or not categories:
        click.echo("Please run 'flask seed-db' first to create initial data.")
        return
    
    # Create test posts
    for i in range(count):
        days_ago = random.randint(0, 30)
        published_at = datetime.utcnow() - timedelta(days=days_ago)
        
        title = fake.sentence(nb_words=6).rstrip('.')
        body_paragraphs = [fake.paragraph(nb_sentences=5) for _ in range(random.randint(3, 8))]
        body = '<p>' + '</p><p>'.join(body_paragraphs) + '</p>'
        
        post = Post(
            title=title,
            slug=slugify(title),
            body=body,
            excerpt=fake.text(max_nb_chars=200),
            status='published',
            views=random.randint(10, 1000),
            author_id=random.choice(users).id,
            category_id=random.choice(categories).id,
            published_at=published_at,
            created_at=published_at - timedelta(hours=random.randint(1, 24))
        )
        
        db.session.add(post)
    
    db.session.commit()
    click.echo(f"Created {count} test posts.")


@click.command()
@with_appcontext
def flush_view_counters():
    """Manually flush view counters from Redis to database."""
    from app.extensions import redis_client
    from app.models.post import Post
    
    # Get all view counter keys from Redis
    keys = redis_client.keys('post:views:*')
    updated_count = 0
    
    for key in keys:
        try:
            post_id = key.decode('utf-8').split(':')[-1]
            view_count = int(redis_client.get(key) or 0)
            
            if view_count > 0:
                post = Post.query.get(post_id)
                if post:
                    post.views += view_count
                    redis_client.delete(key)
                    updated_count += 1
        except Exception as e:
            click.echo(f"Error processing key {key}: {e}")
    
    db.session.commit()
    click.echo(f"Flushed view counters for {updated_count} posts.")


if __name__ == '__main__':
    app = create_cli_app()
    
    # Register commands with the app
    app.cli.add_command(seed_db)
    app.cli.add_command(create_admin)
    app.cli.add_command(clear_cache)
    app.cli.add_command(run_migrations)
    app.cli.add_command(init_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(create_test_data)
    app.cli.add_command(flush_view_counters)
    
    with app.app_context():
        # Run the Flask CLI
        import sys
        if len(sys.argv) > 1:
            app.cli()
        else:
            click.echo("Available commands:")
            click.echo("  flask seed-db")
            click.echo("  flask create-admin --email EMAIL --password PASSWORD")
            click.echo("  flask clear-cache")
            click.echo("  flask run-migrations")
            click.echo("  flask init-db")
            click.echo("  flask drop-db")
            click.echo("  flask create-test-data --count COUNT")
            click.echo("  flask flush-view-counters")
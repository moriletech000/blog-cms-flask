# Blog CMS - Production-Ready Flask Blog System

A complete, production-ready blog management system built with Flask 3.x, featuring a modern tech stack, comprehensive API, background task processing, and Docker deployment.

## 🚀 Features

### Core Functionality
- **Multi-user blog platform** with role-based access control (Reader, Editor, Admin)
- **Rich text editor** support for creating and editing posts
- **Category and tag system** for organizing content
- **Full-text search** using PostgreSQL tsvector
- **Comment system** with threading (one level deep)
- **Like/reaction system** for posts
- **Image upload and processing** with automatic WebP conversion
- **Email notifications** for comments and account actions
- **View counter** with Redis caching

### Technical Features
- **RESTful API** with auto-generated Swagger documentation
- **JWT authentication** for API access
- **Background task processing** with Celery
- **Redis caching** for improved performance
- **Rate limiting** to prevent abuse
- **Docker deployment** with docker-compose
- **Database migrations** with Flask-Migrate
- **Comprehensive test suite** with pytest
- **Error tracking** with Sentry integration

## 📋 Requirements

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

## 🛠️ Installation

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd blog-system
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker compose up --build
```

4. **Initialize the database**
```bash
docker compose exec flask flask db upgrade
docker compose exec flask flask seed-db
```

5. **Access the application**
- Blog: http://localhost
- API Documentation: http://localhost/api/v1/docs
- Admin Panel: http://localhost/admin (login with admin@blog.com / admin123)

### Option 2: Local Development

1. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. **Set up PostgreSQL and Redis**
```bash
# Install PostgreSQL and Redis on your system
# Create database
createdb blogdb
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with local database and Redis URLs
```

4. **Initialize database**
```bash
flask db upgrade
flask seed-db
```

5. **Run the application**
```bash
# Terminal 1: Flask app
flask run

# Terminal 2: Celery worker
celery -A app.extensions.celery worker --loglevel=info

# Terminal 3: Celery beat
celery -A app.extensions.celery beat --loglevel=info
```

## 📁 Project Structure

```
blog-system/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration classes
│   ├── extensions.py            # Flask extensions
│   ├── models/                  # Database models
│   ├── blueprints/              # Route blueprints
│   │   ├── auth/               # Authentication routes
│   │   ├── blog/               # Blog routes
│   │   ├── admin/              # Admin panel routes
│   │   └── api/                # REST API routes
│   ├── schemas/                 # Marshmallow schemas
│   ├── tasks/                   # Celery tasks
│   ├── utils/                   # Utility functions
│   ├── templates/               # Jinja2 templates
│   └── static/                  # Static files
├── tests/                       # Test suite
├── migrations/                  # Database migrations
├── docker/                      # Dockerfiles
├── nginx/                       # Nginx configuration
├── docker-compose.yml           # Docker Compose config
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Flask
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=1

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/blogdb

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
```

## 📚 API Documentation

The API is fully documented with Swagger UI, available at `/api/v1/docs` when the application is running.

### Authentication

```bash
# Get access token
curl -X POST http://localhost/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl http://localhost/api/v1/posts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Key Endpoints

- `POST /api/v1/auth/token` - Login and get JWT tokens
- `GET /api/v1/posts` - List published posts
- `POST /api/v1/posts` - Create new post (editor/admin only)
- `GET /api/v1/posts/<slug>` - Get post details
- `POST /api/v1/posts/<slug>/comments` - Add comment
- `GET /api/v1/categories` - List categories
- `GET /api/v1/tags` - List tags
- `GET /api/v1/users/me` - Get current user profile

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 🔐 Security Features

- **CSRF protection** on all forms
- **Password hashing** with PBKDF2-SHA256
- **Rate limiting** on authentication endpoints
- **JWT tokens** for API authentication
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** with Jinja2 auto-escaping
- **File upload validation** with type and size checks
- **Security headers** via Nginx

## 📊 Database Schema

### Key Models

- **User**: Authentication and profile management
- **Post**: Blog posts with rich content
- **Category**: Post categorization
- **Tag**: Post tagging (many-to-many)
- **Comment**: Threaded comments on posts
- **Like**: Post reactions

### Relationships

- User → Posts (one-to-many)
- User → Comments (one-to-many)
- Post → Category (many-to-one)
- Post ↔ Tags (many-to-many)
- Post → Comments (one-to-many)
- Comment → Comment (self-referential for replies)

## 🎯 CLI Commands

```bash
# Database
flask db upgrade              # Run migrations
flask seed-db                 # Seed initial data
flask init-db                 # Create tables

# User management
flask create-admin --email admin@example.com --password secret

# Maintenance
flask clear-cache             # Clear Redis cache
flask flush-view-counters     # Flush view counts to DB
flask create-test-data --count 20  # Generate test posts
```

## 🚀 Deployment

### Production Checklist

1. **Set secure secrets**
   - Generate strong `FLASK_SECRET_KEY` and `JWT_SECRET_KEY`
   - Use environment-specific `.env` file

2. **Configure email**
   - Set up SMTP credentials
   - Test email delivery

3. **Set up SSL/TLS**
   - Uncomment HTTPS server block in `nginx/nginx.conf`
   - Add SSL certificates to `nginx/ssl/`

4. **Configure Sentry** (optional)
   - Add `SENTRY_DSN` to environment variables

5. **Database backups**
   - Set up automated PostgreSQL backups
   - Test restore procedures

6. **Deploy**
```bash
docker compose -f docker-compose.yml up -d
```

## 📈 Performance Optimization

- **Redis caching** for frequently accessed data
- **Database indexing** on commonly queried fields
- **Image optimization** with Pillow and WebP conversion
- **Nginx static file serving** with caching headers
- **Connection pooling** for database connections
- **Celery task queue** for async operations

## 🐛 Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# View logs
docker compose logs postgres
```

**Celery tasks not executing**
```bash
# Check Celery worker status
docker compose logs celery

# Restart Celery
docker compose restart celery celery-beat
```

**Email not sending**
```bash
# Check Celery logs for email task errors
docker compose logs celery | grep email

# Test SMTP connection
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).starttls()"
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/api/v1/docs`

## 🙏 Acknowledgments

Built with:
- Flask 3.x
- PostgreSQL 16
- Redis 7
- Celery 5.x
- TailwindCSS
- Alpine.js
- Docker

---

**Default Admin Credentials** (after running `flask seed-db`):
- Email: admin@blog.com
- Password: admin123

**⚠️ Change these credentials immediately in production!**
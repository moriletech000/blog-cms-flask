# Blog CMS - Production-Ready Flask Blog System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **complete, production-ready** blog management system built with Flask 3.x. This is not a tutorial or skeleton - every file contains fully implemented, working code ready for deployment.

![Blog CMS Screenshot](https://via.placeholder.com/800x400/6366f1/ffffff?text=Blog+CMS+Dashboard)

## ✨ Features

### Core Functionality
- 🔐 **Multi-user authentication** with role-based access (Reader, Editor, Admin)
- 📝 **Rich text editor** for creating and editing posts
- 🏷️ **Category and tag system** for organizing content
- 🔍 **Full-text search** using PostgreSQL tsvector
- 💬 **Comment system** with threading (one level deep)
- ❤️ **Like/reaction system** for posts
- 🖼️ **Image upload and processing** with automatic WebP conversion
- 📧 **Email notifications** for comments and account actions
- 👁️ **View counter** with Redis caching

### Technical Features
- 🚀 **RESTful API** with auto-generated Swagger documentation
- 🔑 **JWT authentication** for API access
- ⚙️ **Background task processing** with Celery
- ⚡ **Redis caching** for improved performance
- 🛡️ **Rate limiting** to prevent abuse
- 🐳 **Docker deployment** with docker-compose
- 🔄 **Database migrations** with Flask-Migrate
- 🧪 **Comprehensive test suite** with pytest
- 📊 **Error tracking** with Sentry integration

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/moriletech000/blog-cms-flask.git
cd blog-cms-flask

# Start all services
docker compose up --build -d

# Initialize database
docker compose exec flask flask db upgrade
docker compose exec flask flask seed-db

# Access the application
# Blog: http://localhost
# Admin: http://localhost/admin
# API Docs: http://localhost/api/v1/docs
```

**Default Admin Credentials:**
- Email: `admin@blog.com`
- Password: `admin123`

⚠️ **Change these immediately in production!**

### Using Make Commands

```bash
make init      # Build, start, migrate, and seed
make up        # Start services
make down      # Stop services
make logs      # View logs
make test      # Run tests
make shell     # Open Flask shell
```

## 📋 Requirements

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

## 🏗️ Architecture

```
┌─────────────┐
│   Nginx     │ ← Reverse proxy, static files, SSL
└──────┬──────┘
       │
┌──────▼──────┐
│   Flask     │ ← Web application (Gunicorn + gevent)
└──────┬──────┘
       │
       ├─────────┐
       │         │
┌──────▼──────┐ │
│ PostgreSQL  │ │ ← Primary database
└─────────────┘ │
                │
       ┌────────▼────────┐
       │     Redis       │ ← Cache + Celery broker
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │  Celery Worker  │ ← Background tasks
       └─────────────────┘
```

## 📁 Project Structure

```
blog-cms-flask/
├── app/
│   ├── blueprints/          # Route blueprints
│   │   ├── auth/           # Authentication
│   │   ├── blog/           # Blog routes
│   │   ├── admin/          # Admin panel
│   │   └── api/            # REST API
│   ├── models/             # Database models
│   ├── schemas/            # Marshmallow schemas
│   ├── tasks/              # Celery tasks
│   ├── templates/          # Jinja2 templates
│   └── static/             # Static files
├── tests/                  # Test suite
├── docker/                 # Dockerfiles
├── nginx/                  # Nginx configuration
└── docker-compose.yml      # Docker Compose config
```

## 🔐 Security Features

- ✅ CSRF protection on all forms
- ✅ Password hashing (PBKDF2-SHA256)
- ✅ JWT tokens for API
- ✅ Rate limiting (login, register, API)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (Jinja2 auto-escape)
- ✅ File upload validation
- ✅ Security headers (Nginx)
- ✅ Role-based access control

## 📚 API Documentation

The API is fully documented with Swagger UI, available at `/api/v1/docs` when the application is running.

### Key Endpoints

```
POST   /api/v1/auth/token              # Login and get JWT tokens
GET    /api/v1/posts                   # List published posts
POST   /api/v1/posts                   # Create new post (editor/admin)
GET    /api/v1/posts/<slug>            # Get post details
POST   /api/v1/posts/<slug>/comments   # Add comment
GET    /api/v1/categories              # List categories
GET    /api/v1/tags                    # List tags
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 📊 Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Flask 3.0, SQLAlchemy 2.0, PostgreSQL 16 |
| **Cache/Queue** | Redis 7, Celery 5.3 |
| **Frontend** | Jinja2, TailwindCSS, Alpine.js |
| **API** | Flask-RESTX, Marshmallow, JWT |
| **Testing** | pytest, Factory Boy |
| **Deployment** | Docker, Docker Compose, Nginx, Gunicorn |

## 📖 Documentation

- [README.md](README.md) - Complete project documentation
- [QUICKSTART.md](QUICKSTART.md) - 5-minute setup guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows-specific instructions
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete feature overview

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Cache and message broker
- [Celery](https://docs.celeryq.dev/) - Task queue
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [Alpine.js](https://alpinejs.dev/) - JavaScript framework

## 📧 Support

- 📖 Check the [documentation](README.md)
- 🐛 [Open an issue](https://github.com/moriletech000/blog-cms-flask/issues)
- 💬 [Discussions](https://github.com/moriletech000/blog-cms-flask/discussions)

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ using Flask**
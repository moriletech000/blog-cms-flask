# Quick Start Guide

Get your Blog CMS up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- 4GB RAM minimum
- 10GB disk space

## Installation Steps

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd blog-system
```

### 2. Configure Environment

The `.env` file is already configured for Docker Compose. For production, update these values:

```bash
# Edit .env file
nano .env

# Update these critical values:
FLASK_SECRET_KEY=<generate-a-long-random-string>
JWT_SECRET_KEY=<generate-another-long-random-string>
MAIL_USERNAME=<your-smtp-email>
MAIL_PASSWORD=<your-smtp-password>
```

### 3. Start Everything

```bash
# Using Make (recommended)
make init

# Or manually
docker compose up --build -d
docker compose exec flask flask db upgrade
docker compose exec flask flask seed-db
```

### 4. Access the Application

- **Blog Homepage**: http://localhost
- **Admin Panel**: http://localhost/admin
- **API Documentation**: http://localhost/api/v1/docs

**Default Admin Credentials:**
- Email: `admin@blog.com`
- Password: `admin123`

**⚠️ Change these immediately in production!**

## Common Commands

```bash
# View logs
make logs

# Stop services
make down

# Restart services
make restart

# Run tests
make test

# Create a new admin user
make admin

# Access Flask shell
make shell

# Access database shell
make db-shell
```

## Verify Installation

1. **Check all services are running:**
```bash
docker compose ps
```

All services should show "Up" status.

2. **Test the blog:**
- Visit http://localhost
- You should see the blog homepage with sample posts

3. **Test admin panel:**
- Visit http://localhost/admin
- Login with admin@blog.com / admin123
- You should see the dashboard

4. **Test API:**
- Visit http://localhost/api/v1/docs
- You should see Swagger UI documentation

## Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs

# Restart everything
docker compose down
docker compose up --build
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Restart PostgreSQL
docker compose restart postgres

# Wait a few seconds and try again
```

### Can't access the site

```bash
# Check if port 80 is available
sudo lsof -i :80

# If port 80 is in use, edit docker-compose.yml
# Change "80:80" to "8080:80" under nginx ports
# Then access at http://localhost:8080
```

### Email not sending

Email functionality requires valid SMTP credentials. For development:
- Use a Gmail account with an App Password
- Or use a service like Mailtrap for testing
- Or check Celery logs: `docker compose logs celery`

## Next Steps

1. **Change admin password:**
   - Login to admin panel
   - Go to Profile
   - Update password

2. **Configure email:**
   - Update MAIL_* variables in `.env`
   - Restart services: `make restart`

3. **Create content:**
   - Login to admin panel
   - Create categories
   - Create your first post
   - Publish it!

4. **Customize:**
   - Edit templates in `app/templates/`
   - Modify styles in `app/static/css/custom.css`
   - Restart Flask: `docker compose restart flask`

## Production Deployment

For production deployment:

1. **Update environment variables:**
   - Set `FLASK_ENV=production`
   - Generate strong secrets
   - Configure real SMTP server
   - Set up Sentry DSN (optional)

2. **Enable HTTPS:**
   - Uncomment HTTPS server block in `nginx/nginx.conf`
   - Add SSL certificates to `nginx/ssl/`

3. **Set up backups:**
   - Configure PostgreSQL backups
   - Backup uploaded images regularly

4. **Monitor:**
   - Set up log aggregation
   - Configure Sentry for error tracking
   - Monitor resource usage

## Support

- Check the main README.md for detailed documentation
- Review API docs at /api/v1/docs
- Check logs: `make logs`
- Open an issue on GitHub

## Development Mode

To run in development mode with hot reload:

```bash
# Use the override file (automatically used)
docker compose up

# Flask will run with debug mode enabled
# Code changes will auto-reload
```

---

**Happy Blogging! 🚀**
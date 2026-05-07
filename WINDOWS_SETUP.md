# Running Blog CMS on Windows

## Option 1: Docker Desktop (Recommended)

### Step 1: Install Docker Desktop

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Restart your computer
4. Start Docker Desktop
5. Wait for Docker to fully start (check system tray icon)

### Step 2: Start the Application

Open PowerShell in the project directory and run:

```powershell
# Build and start all services
docker compose up --build -d

# Wait for services to start (about 30 seconds)
Start-Sleep -Seconds 30

# Initialize database
docker compose exec flask flask db upgrade
docker compose exec flask flask seed-db

# Check status
docker compose ps
```

### Step 3: Access the Application

- Blog: http://localhost
- Admin Panel: http://localhost/admin
- API Docs: http://localhost/api/v1/docs

**Default Admin Login:**
- Email: admin@blog.com
- Password: admin123

---

## Option 2: Local Python Installation (Without Docker)

If you prefer not to use Docker, you can run locally:

### Prerequisites

1. **Python 3.12**: Download from https://www.python.org/downloads/
2. **PostgreSQL 16**: Download from https://www.postgresql.org/download/windows/
3. **Redis**: Download from https://github.com/microsoftarchive/redis/releases

### Step 1: Install PostgreSQL

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE blogdb;
CREATE USER bloguser WITH PASSWORD 'blogpass';
GRANT ALL PRIVILEGES ON DATABASE blogdb TO bloguser;
```

### Step 2: Install Redis

1. Download Redis for Windows
2. Extract and run `redis-server.exe`

### Step 3: Set Up Python Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

Edit `.env` file and update these values:

```bash
# Use local services instead of Docker
DATABASE_URL=postgresql://bloguser:blogpass@localhost:5432/blogdb
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
RATELIMIT_STORAGE_URI=redis://localhost:6379/2
```

### Step 5: Initialize Database

```powershell
# Initialize migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed database
flask seed-db
```

### Step 6: Run the Application

Open 3 separate PowerShell windows:

**Window 1 - Flask App:**
```powershell
.\venv\Scripts\Activate.ps1
$env:FLASK_APP="wsgi.py"
flask run --host=0.0.0.0 --port=5000
```

**Window 2 - Celery Worker:**
```powershell
.\venv\Scripts\Activate.ps1
celery -A app.extensions.celery worker --loglevel=info --pool=solo
```

**Window 3 - Celery Beat:**
```powershell
.\venv\Scripts\Activate.ps1
celery -A app.extensions.celery beat --loglevel=info
```

### Step 7: Access the Application

- Blog: http://localhost:5000
- Admin Panel: http://localhost:5000/admin
- API Docs: http://localhost:5000/api/v1/docs

---

## Option 3: Use WSL2 (Windows Subsystem for Linux)

### Step 1: Install WSL2

```powershell
# Run as Administrator
wsl --install
```

### Step 2: Install Docker in WSL2

```bash
# In WSL2 terminal
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo service docker start
```

### Step 3: Run the Application

```bash
cd /mnt/c/path/to/blog-system
docker compose up --build -d
docker compose exec flask flask db upgrade
docker compose exec flask flask seed-db
```

---

## Troubleshooting

### Port Already in Use

If port 80 is already in use, edit `docker-compose.yml`:

```yaml
nginx:
  ports:
    - "8080:80"  # Change 80 to 8080
```

Then access at http://localhost:8080

### PostgreSQL Connection Issues

Make sure PostgreSQL is running:
```powershell
# Check if PostgreSQL service is running
Get-Service -Name postgresql*
```

### Redis Connection Issues

Make sure Redis is running:
```powershell
# Start Redis
.\redis-server.exe
```

### Permission Issues

Run PowerShell as Administrator if you encounter permission errors.

---

## Quick Commands

### Docker Commands

```powershell
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart a service
docker compose restart flask

# Access Flask shell
docker compose exec flask flask shell

# Run tests
docker compose exec flask pytest tests/ -v
```

### Local Development Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run Flask
flask run

# Run tests
pytest tests/ -v

# Create admin user
flask create-admin --email admin@example.com --password yourpassword

# Clear cache
flask clear-cache
```

---

## Next Steps

1. Change the default admin password
2. Configure email settings in `.env`
3. Start creating content!

For more information, see:
- README.md - Complete documentation
- QUICKSTART.md - Quick setup guide
- DEPLOYMENT.md - Production deployment
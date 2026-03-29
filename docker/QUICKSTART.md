# Quick Start - Docker Server

Get your Garmin Workout Creator server running in 5 minutes!

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- Google Gemini API key ([Get free key](https://aistudio.google.com/apikey))

## Option 1: Automated Setup (Recommended)

```bash
cd docker
./setup-server.sh
```

The script will:
1. Generate security keys automatically
2. Create `.env` file from template
3. Prompt you to add API keys
4. Build and start all services
5. Display access URLs

**That's it!** Your server is running.

## Option 2: Manual Setup

### 1. Configure Environment

```bash
cd docker
cp .env.example .env
```

### 2. Generate Security Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate ENCRYPTION_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Edit .env File

Add the generated keys and your API keys:
```bash
nano .env  # or use your favorite editor
```

Required values:
- `SECRET_KEY` - Paste generated secret key
- `ENCRYPTION_KEY` - Paste generated encryption key
- `GOOGLE_API_KEY` - Your Gemini API key
- `DB_USER` - Database username (e.g., `garmin_admin`)
- `DB_PASSWORD` - Strong database password

### 4. Start the Server

**Development mode (with hot reload):**
```bash
docker-compose up -d
```

**Production mode:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Verify It's Running

```bash
docker-compose ps
```

All services should show "Up" and "healthy" status.

## Access Your Application

- **Web Interface:** http://localhost
- **API Endpoint:** http://localhost/api
- **Health Check:** http://localhost/health
- **API Docs:** http://localhost/api/docs (FastAPI auto-generated)

## Common Commands

```bash
# View logs (all services)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Stop the server
docker-compose down

# Restart services
docker-compose restart

# Update after code changes
docker-compose build
docker-compose up -d
```

## Troubleshooting

### "Port already in use"
```bash
# Check what's using port 80
lsof -i :80

# Or use different port (edit docker-compose.yml)
# Change "80:80" to "8080:80"
```

### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop
# Or on Linux:
sudo systemctl start docker
```

### Services not healthy
```bash
# Check individual service logs
docker-compose logs backend
docker-compose logs postgres

# Restart unhealthy service
docker-compose restart backend
```

### Database connection error
```bash
# Verify database is running
docker-compose ps postgres

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

## What's Running?

| Service | Internal Port | External Access |
|---------|---------------|-----------------|
| Nginx | 80 | http://localhost |
| Backend (FastAPI) | 8000 | http://localhost/api |
| Frontend (React) | 5173/80 | http://localhost |
| PostgreSQL | 5432 | Internal only |

## Next Steps

1. **Test the API:**
   - Visit http://localhost/health
   - Visit http://localhost/api/docs for interactive API documentation

2. **Create your first workout:**
   - Open http://localhost in your browser
   - Register an account (Phase 2)
   - Connect your Garmin account (Phase 2)
   - Create a workout! (Phase 2)

3. **Monitor your server:**
   ```bash
   # Watch logs in real-time
   docker-compose logs -f

   # Check resource usage
   docker stats
   ```

## Configuration

All configuration is in `docker/.env`:

```bash
# View current configuration
cat .env

# Edit configuration
nano .env

# Apply changes (restart services)
docker-compose down
docker-compose up -d
```

## Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U garmin_admin garmin_workouts > backup.sql

# Restore backup
cat backup.sql | docker-compose exec -T postgres psql -U garmin_admin garmin_workouts
```

## Updating the Application

When new code is pushed:

```bash
# Pull latest code
git pull

# Rebuild and restart
cd docker
docker-compose build
docker-compose up -d
```

## Security Notes

⚠️ **For production deployment:**

1. Change default passwords in `.env`
2. Set up SSL/HTTPS (see `docker/README.md`)
3. Configure firewall to restrict access
4. Set up regular database backups
5. Use strong, unique passwords
6. Don't commit `.env` file to git

## Getting Help

- **Full documentation:** `docker/README.md`
- **Implementation plan:** `../IMPLEMENTATION_PLAN.md`
- **Phase 1 docs:** `../docs/PHASE_1_SETUP.md`

## Clean Shutdown

To completely stop and remove everything:

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes database!)
docker-compose down -v

# Remove images too
docker-compose down -v --rmi all
```

---

**Ready to go?** Run `./setup-server.sh` and your server will be up in minutes! 🚀

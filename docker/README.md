# Docker Server Setup

This Docker configuration provides a complete, production-ready server environment for the Garmin Workout Creator application.

## Overview

The setup includes:
- **PostgreSQL** - Database with persistent storage
- **Backend** - FastAPI application
- **Frontend** - React application (production build)
- **Nginx** - Reverse proxy with rate limiting and SSL support
- **Health checks** - All services monitored
- **Auto-restart** - Services restart on failure

## Quick Start

### 1. Configure Environment

```bash
cd docker
cp .env.example .env
# Edit .env and add your values
```

**Required values:**
```bash
# Generate these keys:
openssl rand -hex 32  # For SECRET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # For ENCRYPTION_KEY

# Add your API keys:
# - GOOGLE_API_KEY (from https://aistudio.google.com/apikey)
# - DB_USER and DB_PASSWORD (create secure credentials)
```

### 2. Start the Server

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Access the Application

- **Frontend:** http://localhost
- **API:** http://localhost/api
- **Health Check:** http://localhost/health

### 4. Stop the Server

```bash
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes database)
docker-compose -f docker-compose.prod.yml down -v
```

## Services

### PostgreSQL (Database)
- **Port:** 5432 (internal only)
- **Data:** Persisted in `postgres_data` volume
- **Backup location:** `./postgres-backup/`
- **Health check:** Every 10 seconds

### Backend (FastAPI)
- **Port:** 8000 (internal only)
- **Access:** Via Nginx at `/api`
- **Health check:** Every 30 seconds
- **Auto-restart:** Yes

### Frontend (React + Nginx)
- **Port:** 80 (internal only)
- **Access:** Via main Nginx
- **Static files:** Optimized production build
- **Health check:** Every 30 seconds

### Nginx (Reverse Proxy)
- **Ports:** 80 (HTTP), 443 (HTTPS - requires SSL)
- **Features:**
  - Rate limiting (60 requests/min per IP)
  - Login rate limiting (5 attempts/min)
  - Gzip compression
  - Static file caching (1 year)
  - Security headers
  - Request size limit: 10MB
- **Logs:** `nginx_logs` volume

## Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production service definitions |
| `docker-compose.yml` | Development service definitions |
| `nginx-prod.conf` | Nginx reverse proxy configuration |
| `backend.Dockerfile` | Backend container image |
| `frontend.Dockerfile.prod` | Frontend production container |
| `.env` | Environment variables (create from .env.example) |

## Network Architecture

```
Internet
    ↓
Nginx (Port 80/443)
    ├─→ /api/* → Backend (FastAPI) → PostgreSQL
    └─→ /*     → Frontend (React Static Files)
```

All services communicate on internal `garmin_network` bridge network.

## Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f postgres
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Restart Services
```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Execute Commands in Containers
```bash
# Access backend shell
docker-compose -f docker-compose.prod.yml exec backend sh

# Access database
docker-compose -f docker-compose.prod.yml exec postgres psql -U garmin_admin -d garmin_workouts

# View nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/nginx.conf
```

### Database Management

#### Backup Database
```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U garmin_admin garmin_workouts > backup.sql

# Or automated backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U garmin_admin garmin_workouts > ./postgres-backup/backup-$(date +%Y%m%d-%H%M%S).sql
```

#### Restore Database
```bash
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T postgres psql -U garmin_admin garmin_workouts
```

#### Reset Database (WARNING: Deletes all data)
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

## Health Monitoring

All services have health checks:

```bash
# Check service health
docker-compose -f docker-compose.prod.yml ps
```

Health endpoints:
- **Overall:** `http://localhost/health`
- **Backend:** `http://localhost/api/health`

## Updating the Application

### Update Backend Code
```bash
# Rebuild and restart backend
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend
```

### Update Frontend Code
```bash
# Rebuild and restart frontend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Update All Services
```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## SSL/HTTPS Setup (Optional)

### 1. Get SSL Certificate

**Option A: Let's Encrypt (Free)**
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com
```

**Option B: Self-Signed (Development)**
```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem
```

### 2. Configure Nginx for HTTPS

Edit `nginx-prod.conf` and uncomment the HTTPS server block. Update `server_name` with your domain.

### 3. Restart Nginx
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service_name

# Check if port is already in use
lsof -i :80
lsof -i :443
```

### Database connection issues
```bash
# Verify database is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U garmin_admin -d garmin_workouts -c '\l'
```

### Backend errors
```bash
# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Cannot access application
```bash
# Check nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Verify nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Check if all services are healthy
docker-compose -f docker-compose.prod.yml ps
```

## Performance Tuning

### Adjust Worker Processes
Edit `nginx-prod.conf`:
```nginx
worker_processes 4;  # Set to number of CPU cores
```

### Increase Rate Limits
Edit `nginx-prod.conf`:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=120r/m;  # Increase from 60
```

### Database Connection Pooling
Backend environment variable (in `docker-compose.prod.yml`):
```yaml
DATABASE_POOL_SIZE: 20
DATABASE_MAX_OVERFLOW: 10
```

## Security Checklist

- [ ] Changed default database password
- [ ] Generated strong SECRET_KEY
- [ ] Generated strong ENCRYPTION_KEY
- [ ] Configured firewall (only ports 80/443 open)
- [ ] SSL certificate installed (for production)
- [ ] Regular database backups configured
- [ ] Monitoring setup (logs, health checks)
- [ ] Updated all API keys
- [ ] Restricted CORS origins
- [ ] Rate limiting configured

## Monitoring

### Resource Usage
```bash
# CPU and memory
docker stats

# Disk usage
docker system df
```

### Log Rotation
Configure log rotation to prevent disk space issues:

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/docker-logs
```

Add:
```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    delaycompress
    missingok
    notifempty
}
```

## Moving to Production Server

When ready to deploy to a real server:

1. **Copy files to server:**
   ```bash
   scp -r docker/ user@your-server:/path/to/app/
   ```

2. **Install Docker on server:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

3. **Configure .env on server** with production values

4. **Start services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Configure domain DNS** to point to server IP

6. **Set up SSL** with Let's Encrypt

## Support

For issues or questions, refer to:
- Main documentation: `../IMPLEMENTATION_PLAN.md`
- Phase documentation: `../docs/PHASE_1_SETUP.md`

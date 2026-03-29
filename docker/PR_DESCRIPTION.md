# Docker Production Server Setup

## Summary
Complete Docker-based server environment that can run locally as a temporary production server. Includes all services, automated setup, and production optimizations.

## What's Included

### 🐳 Production Docker Compose
- **PostgreSQL** - Database with persistent storage and backups
- **Backend** - FastAPI with health checks and auto-restart
- **Frontend** - Production-optimized React build
- **Nginx** - Reverse proxy with rate limiting and security

### 🚀 One-Command Setup
```bash
cd docker
./setup-server.sh
```

Automated script that:
- Generates security keys
- Creates environment configuration
- Builds and starts all services
- Verifies health status

### 📋 Features
- **Health checks** - All services monitored
- **Auto-restart** - Services recover from failures
- **Rate limiting** - API (60/min), Login (5/min)
- **Security headers** - HSTS, CSP, XSS protection
- **Gzip compression** - Faster response times
- **Static caching** - 1-year cache for assets
- **Database backups** - Easy backup/restore commands
- **SSL ready** - Just add certificates

### 📁 New Files
- `docker-compose.prod.yml` - Production services
- `nginx-prod.conf` - Nginx configuration
- `frontend.Dockerfile.prod` - Optimized frontend build
- `setup-server.sh` - Automated setup script
- `README.md` - Complete documentation
- `QUICKSTART.md` - 5-minute setup guide
- `.env.example` - Environment template

## Quick Start

```bash
cd docker
./setup-server.sh
```

Then access:
- Frontend: http://localhost
- API: http://localhost/api
- Health: http://localhost/health

## Network Architecture

```
Internet → Nginx (Port 80/443)
              ├─→ /api/* → Backend → PostgreSQL
              └─→ /*     → Frontend
```

All services on internal bridge network.

## Management Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Stop server
docker-compose -f docker-compose.prod.yml down

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U garmin_admin garmin_workouts > backup.sql
```

## Production Ready

This setup can run:
- ✅ Locally as temporary server
- ✅ On any server with Docker
- ✅ On cloud VPS (DigitalOcean, Linode, etc.)
- ✅ With or without domain name

## Next Steps

After merging:
1. Run `./setup-server.sh`
2. Add your Google API key
3. Access http://localhost
4. Server is ready!

When ready for real server:
- Copy to production server
- Add SSL certificates
- Configure domain DNS
- Enable HTTPS in nginx config

## Documentation

Full details in:
- `docker/QUICKSTART.md` - Quick setup
- `docker/README.md` - Complete guide

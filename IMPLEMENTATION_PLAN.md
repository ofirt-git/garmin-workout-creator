# Garmin Workout Creator - Web Application Implementation Plan

## 📋 Executive Summary

Transform the CLI tool into a secure, production-ready web application that allows users to:
- Create workouts from natural language
- Securely connect their Garmin accounts
- Upload workouts directly to Garmin Connect
- Manage their workout history

**Estimated Timeline:** 6-8 weeks (part-time)
**Tech Stack:** FastAPI (backend) + React (frontend) + PostgreSQL
**Deployment:** Railway.app or Render.com (recommended for MVP)

---

## 🎯 Project Phases Overview

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 1** | Week 1 | Project Setup & Infrastructure |
| **Phase 2** | Week 2-3 | Backend Core Development |
| **Phase 3** | Week 4-5 | Frontend Development |
| **Phase 4** | Week 6 | Security & Authentication |
| **Phase 5** | Week 7-8 | Testing & Deployment |

---

# Phase 1: Project Setup & Infrastructure (Week 1)

## Goals
- Restructure repository for web app
- Set up development environment
- Create database schema
- Configure environment variables
- Install core dependencies

## 1.1 Repository Restructure

Transform current CLI-focused structure into monorepo:

```
garmin-workout-creator/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # Business logic layer
│   │   ├── core/              # Security, config, utilities
│   │   └── middleware/        # Rate limiting, logging
│   ├── alembic/               # Database migrations
│   ├── tests/
│   └── requirements.txt
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page-level components
│   │   ├── services/          # API client services
│   │   ├── context/           # React context (auth, state)
│   │   └── hooks/             # Custom React hooks
│   └── package.json
│
├── shared/                     # Shared code (existing parsers/uploaders)
│   ├── workout_parser/
│   └── garmin_uploader/
│
├── cli/                        # Keep existing CLI separate
├── docker/                     # Docker configurations
└── docs/                       # Documentation
```

## 1.2 Environment Configuration

### Backend Environment Variables
- **Application:** App name, environment (dev/prod), debug mode
- **Database:** PostgreSQL connection URL, pool settings
- **Security:** JWT secret key, token expiration settings
- **Encryption:** Fernet key for Garmin token encryption
- **API Keys:** Google Gemini API key (server-side only)
- **CORS:** Allowed frontend origins
- **Rate Limiting:** Requests per minute/hour limits

### Frontend Environment Variables
- **API Base URL:** Backend API endpoint
- **App Configuration:** Name, environment

### Security Key Generation
```bash
# JWT Secret Key
openssl rand -hex 32

# Encryption Key for Garmin tokens
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 1.3 Database Setup

### Install PostgreSQL
Options:
- Local installation (brew/apt)
- Docker container
- Managed service (for production)

### Database Schema Design

**Core Tables:**
1. **users** - User accounts with email/password
2. **garmin_auth** - Encrypted Garmin OAuth tokens per user
3. **workouts** - Workout history with original text and parsed JSON
4. **api_usage** - Rate limiting and usage tracking

**Key Features:**
- UUID primary keys
- Foreign key relationships with cascade deletes
- Timestamps for all tables
- Indexes on frequently queried fields
- JSONB for flexible workout storage

## 1.4 Dependencies Installation

### Backend Core Dependencies
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **cryptography** - Token encryption
- **Existing:** anthropic, google-genai, garth, pydantic

### Frontend Core Dependencies
- **React** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Tailwind CSS** - Styling
- **React Hot Toast** - Notifications
- **Vite** - Build tool

## Success Criteria - Phase 1
- [ ] Repository restructured with new folders
- [ ] PostgreSQL database created and accessible
- [ ] All dependencies installed successfully
- [ ] Environment variables configured
- [ ] Database schema created via migration
- [ ] Backend server starts without errors
- [ ] Frontend dev server runs successfully

---

# Phase 2: Backend Core Development (Week 2-3)

## Goals
- Implement user authentication system
- Create Garmin connection service with secure token storage
- Build workout parsing and upload endpoints
- Set up database models and migrations
- Implement core business logic

## 2.1 Authentication System

### User Management
- User registration with email/password
- Password hashing using bcrypt
- Email validation
- User profile management

### JWT Authentication
- Access token generation (short-lived, 30 min)
- Refresh token mechanism (long-lived, 7 days)
- Token validation middleware
- Automatic token refresh on expiry

### API Endpoints
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

## 2.2 Garmin Integration Service

### Secure Connection Flow
1. User provides Garmin credentials (email/password)
2. Backend authenticates with Garmin API
3. Receives OAuth1 and OAuth2 tokens from Garmin
4. **Immediately discards password** from memory
5. Encrypts tokens using Fernet encryption
6. Stores encrypted tokens in database
7. Returns success response to frontend

### Token Management
- Encrypt tokens before database storage
- Decrypt tokens only when needed for API calls
- Test token validity before operations
- Handle token expiration gracefully
- Update last verified timestamp

### API Endpoints
- `POST /api/garmin/connect` - Connect Garmin account
- `GET /api/garmin/status` - Check connection status
- `DELETE /api/garmin/disconnect` - Remove stored credentials

## 2.3 Workout Service

### Workout Operations
- Parse natural language using existing parsers
- Use YOUR Google API key (server-side)
- Validate workout JSON structure
- Upload to Garmin using stored tokens
- Save workout history to database
- Retrieve user's workout history

### API Endpoints
- `POST /api/workouts/parse` - Parse text to JSON (preview only)
- `POST /api/workouts/create` - Parse and upload to Garmin
- `GET /api/workouts` - Get user's workout history
- `GET /api/workouts/{id}` - Get specific workout details

## 2.4 Database Models

### Key Models
- **User Model:** Authentication and profile data
- **GarminAuth Model:** Encrypted token storage with user relationship
- **Workout Model:** Complete workout data with JSONB field
- **APIUsage Model:** Rate limiting tracking

### Relationships
- One user → One Garmin auth (one-to-one)
- One user → Many workouts (one-to-many)
- Cascade deletes for data cleanup

## 2.5 Core Services Layer

### Authentication Service
- Handle user registration logic
- Manage login authentication
- Token generation and validation
- Password reset functionality (future)

### Garmin Service
- Manage Garmin OAuth flow
- Handle token encryption/decryption
- Test connection validity
- Interface with garth library

### Workout Service
- Parse workout text via Gemini
- Transform to Garmin format
- Upload via Garmin client
- Store workout history
- Retrieve and filter workouts

### Encryption Service
- Centralized encryption/decryption
- Secure key management
- Token handling utilities

## Success Criteria - Phase 2
- [ ] Users can register and login
- [ ] JWT tokens generated and validated
- [ ] Users can connect Garmin account
- [ ] Garmin tokens encrypted in database
- [ ] Workout parsing endpoint functional
- [ ] Workouts upload to Garmin successfully
- [ ] Workout history retrievable
- [ ] All endpoints tested with API client (Postman/curl)
- [ ] Database migrations working

---

# Phase 3: Frontend Development (Week 4-5)

## Goals
- Create responsive UI with React
- Implement authentication flows
- Build Garmin connection interface
- Design workout creator interface
- Integrate with backend API
- Handle loading states and errors

## 3.1 Core UI Components

### Authentication Components
- **LoginForm** - Email/password login
- **RegisterForm** - Account creation
- **ProtectedRoute** - Route guard for authenticated pages

### Garmin Components
- **GarminConnectModal** - Secure credential entry
- **ConnectionStatus** - Display connection state
- **DisconnectButton** - Remove Garmin connection

### Workout Components
- **WorkoutCreator** - Text input and parsing
- **WorkoutPreview** - Display parsed workout structure
- **WorkoutHistory** - List past workouts
- **WorkoutCard** - Individual workout display

### Layout Components
- **Header** - Navigation and user menu
- **Footer** - App info
- **Sidebar** - Navigation menu
- **LoadingSpinner** - Loading states

## 3.2 Page Structure

### Public Pages
- **HomePage** - Landing page with features
- **LoginPage** - User login
- **RegisterPage** - New user signup

### Protected Pages (Require Auth)
- **DashboardPage** - Main app interface
- **CreateWorkoutPage** - Workout creation
- **HistoryPage** - Past workouts
- **SettingsPage** - User preferences and Garmin connection

## 3.3 State Management

### React Context
- **AuthContext** - User authentication state
- **GarminContext** - Garmin connection status
- **WorkoutContext** - Current workout state (optional)

### Custom Hooks
- **useAuth** - Authentication operations
- **useGarmin** - Garmin operations
- **useWorkouts** - Workout CRUD operations

## 3.4 API Integration

### API Client Setup
- Axios instance with base configuration
- Automatic JWT token injection
- Token refresh interceptor
- Error handling interceptor

### Service Modules
- **authService** - Registration, login, user management
- **garminService** - Connect, status, disconnect
- **workoutService** - Parse, create, retrieve workouts

## 3.5 User Experience Features

### Loading States
- Skeleton loaders during data fetch
- Button loading indicators
- Progress indicators for long operations

### Error Handling
- Toast notifications for success/error
- Form validation messages
- API error display
- Retry mechanisms

### Responsive Design
- Mobile-first approach
- Tailwind CSS utility classes
- Responsive navigation
- Touch-friendly interactions

## 3.6 Key User Flows

### First-Time User Flow
1. Land on homepage
2. Register account
3. Connect Garmin account via modal
4. Create first workout
5. See success message with Garmin link

### Returning User Flow
1. Login
2. Dashboard shows workout history
3. Create new workout
4. Instantly uploads (tokens already stored)

### Workout Creation Flow
1. Enter workout description
2. Click "Parse" to preview
3. Review parsed structure
4. Click "Upload to Garmin"
5. Success message with Garmin URL

## Success Criteria - Phase 3
- [ ] User can register via UI
- [ ] User can login and stay authenticated
- [ ] Protected routes redirect to login
- [ ] Garmin connection modal works
- [ ] Workout creation interface functional
- [ ] Workout preview displays correctly
- [ ] Workouts upload successfully
- [ ] History page shows past workouts
- [ ] Responsive on mobile devices
- [ ] Loading states work properly
- [ ] Errors display to user

---

# Phase 4: Security & Authentication (Week 6)

## Goals
- Harden security across application
- Implement rate limiting
- Add input validation
- Set up monitoring
- Conduct security audit

## 4.1 Security Hardening

### Authentication Security
- Strong password requirements (min 8 chars, complexity)
- Password hashing with bcrypt (cost factor 12)
- JWT token expiration enforcement
- Secure token storage (httpOnly cookies option)
- Refresh token rotation
- Rate limiting on login attempts (prevent brute force)

### API Security
- HTTPS only in production
- CORS configuration (whitelist frontend domain)
- Rate limiting per endpoint
- Request size limits
- SQL injection prevention (ORM parameterization)
- XSS prevention (input sanitization)
- CSRF protection

### Data Security
- Garmin token encryption at rest (Fernet AES-128)
- Environment variables for secrets
- No secrets in code or version control
- Database connection over SSL
- Secure session management

### Infrastructure Security
- Security headers (HSTS, CSP, X-Frame-Options)
- DDoS protection via hosting provider
- Regular dependency updates
- Vulnerability scanning

## 4.2 Rate Limiting

### Implementation Strategy
- Per-user rate limits stored in database
- Sliding window algorithm
- Different limits per endpoint type:
  - Login: 5 attempts per 15 minutes
  - Workout creation: 20 per hour
  - API calls: 100 per hour

### Response Handling
- Return 429 status code when exceeded
- Include retry-after header
- Clear user feedback on frontend

## 4.3 Input Validation

### Backend Validation
- Pydantic schemas for all request/response
- Email format validation
- Password strength requirements
- Workout text length limits
- JSON structure validation

### Frontend Validation
- Form validation with React Hook Form
- Real-time validation feedback
- Client-side checks before API calls
- Sanitize user inputs

## 4.4 Monitoring & Logging

### Logging Strategy
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Authentication events
- Error tracking

### What to Log
- API requests (method, path, status, duration)
- Authentication attempts (success/failure)
- Garmin connection events
- Workout operations
- Errors and exceptions

### What NOT to Log
- Passwords
- Raw tokens
- Sensitive personal data

### Monitoring Tools (Optional)
- **Sentry** - Error tracking
- **LogRocket** - Session replay
- **Uptime monitoring** - Health checks

## 4.5 Security Audit Checklist

### Authentication
- [x] Passwords hashed with bcrypt
- [x] JWT tokens properly validated
- [x] Token expiration enforced
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Password reset flow (future feature)

### Data Protection
- [x] Garmin tokens encrypted at rest
- [x] Secure environment variable management
- [x] No secrets in git repository
- [ ] Database backups enabled
- [ ] Audit logging implemented

### API Security
- [x] CORS properly configured
- [x] Input validation on all endpoints
- [ ] Rate limiting per user
- [ ] Request size limits
- [ ] CSRF protection for state-changing operations

### Infrastructure
- [ ] HTTPS/TLS in production
- [ ] Security headers configured
- [ ] Regular security updates scheduled
- [ ] Vulnerability scanning enabled

## Success Criteria - Phase 4
- [ ] All authentication endpoints secured
- [ ] Rate limiting implemented and tested
- [ ] Input validation on all forms
- [ ] Logging system configured
- [ ] Security checklist 90% complete
- [ ] No high-severity vulnerabilities
- [ ] Password requirements enforced
- [ ] Token encryption verified

---

# Phase 5: Testing & Deployment (Week 7-8)

## Goals
- Write comprehensive tests
- Set up CI/CD pipeline
- Configure production environment
- Deploy to hosting platform
- Set up monitoring and backups

## 5.1 Testing Strategy

### Backend Testing

**Unit Tests**
- Test individual functions in isolation
- Mock external dependencies
- Focus on business logic
- Coverage target: 70%+

**Integration Tests**
- Test API endpoints end-to-end
- Use test database
- Test authentication flows
- Test Garmin integration (mocked)
- Test workout operations

**Test Structure**
- Test user registration/login
- Test token generation/validation
- Test Garmin connection flow
- Test workout parsing
- Test workout upload
- Test error handling

### Frontend Testing

**Component Tests**
- Test component rendering
- Test user interactions
- Test form submissions
- Mock API calls

**Integration Tests**
- Test complete user flows
- Test authentication flow
- Test workout creation flow
- Test error scenarios

**Key Test Scenarios**
- User registration and login
- Garmin connection modal
- Workout creation and preview
- Error message display

## 5.2 Docker Configuration

### Container Setup
- **Backend container:** Python + FastAPI
- **Frontend container:** Node build → Nginx serve
- **Database container:** PostgreSQL
- **Docker Compose** for local development

### Container Features
- Multi-stage builds for smaller images
- Health checks for all services
- Volume mounts for development
- Environment variable injection
- Network isolation

## 5.3 Deployment Options

### Option A: Railway.app (Recommended for MVP)

**Pros:**
- Free tier available ($5/month credit)
- Automatic HTTPS
- PostgreSQL included
- GitHub auto-deploy
- Zero configuration
- Built-in monitoring

**Setup:**
1. Connect GitHub repository
2. Add PostgreSQL database
3. Set environment variables
4. Deploy with one click

**Cost:** Free tier → ~$10-20/month for production

### Option B: Render.com

**Pros:**
- Free tier with limitations
- Automatic SSL
- PostgreSQL included (paid)
- Git-based deployments
- Good documentation

**Setup:**
1. Create render.yaml configuration
2. Connect repository
3. Configure services
4. Auto-deploy on push

**Cost:** Free tier → ~$7/month for database

### Option C: Vercel (Frontend) + Railway (Backend)

**Best of both worlds:**
- Vercel for frontend (free, fast CDN)
- Railway for backend + database

**Pros:**
- Excellent frontend performance
- Simple backend management
- Good free tiers

### Option D: AWS/GCP/Azure (Production-Scale)

**For future growth:**
- AWS ECS/Fargate for containers
- RDS for PostgreSQL
- CloudFront for CDN
- Route53 for DNS
- Load balancer for scaling

**Cost:** ~$50-100+/month

## 5.4 Production Configuration

### Environment Setup
- Production environment variables
- Strong SECRET_KEY and ENCRYPTION_KEY
- Database connection pooling
- CORS restricted to production domain
- Debug mode OFF
- Logging level: INFO or WARNING

### Database
- Enable SSL connections
- Set up automated backups
- Configure connection pooling
- Enable query monitoring

### Security Hardening
- Force HTTPS
- Set security headers
- Enable rate limiting
- Configure firewall rules
- Set up DDoS protection

## 5.5 CI/CD Pipeline

### GitHub Actions Workflow
1. **On Push:**
   - Run backend tests
   - Run frontend tests
   - Check code formatting
   - Run linting

2. **On Pull Request:**
   - Run full test suite
   - Check test coverage
   - Security scan

3. **On Merge to Main:**
   - Build Docker images
   - Deploy to production
   - Run smoke tests

### Deployment Process
1. Push to main branch
2. CI tests pass
3. Build containers
4. Deploy to hosting
5. Health check verification
6. Rollback on failure

## 5.6 Monitoring & Maintenance

### Health Monitoring
- Backend health endpoint (`/health`)
- Database connectivity check
- External service status (Garmin API)
- Uptime monitoring (UptimeRobot, Pingdom)

### Performance Monitoring
- API response times
- Database query performance
- Error rates
- User activity metrics

### Backup Strategy
- Daily database backups
- Retain 7 days of backups
- Test restoration process
- Store backups in separate location

### Maintenance Tasks
- Weekly: Review logs and errors
- Monthly: Update dependencies
- Quarterly: Security audit
- Ongoing: Monitor user feedback

## Success Criteria - Phase 5
- [ ] Test coverage >70% backend
- [ ] All critical paths tested
- [ ] Docker containers build successfully
- [ ] Application deployed to production
- [ ] HTTPS configured and working
- [ ] Database backups enabled
- [ ] Monitoring/logging active
- [ ] Health checks passing
- [ ] Documentation complete
- [ ] Rollback procedure tested

---

# Post-Launch Roadmap (Phase 6+)

## Short-Term Enhancements (Month 2-3)
- Email verification for new users
- Password reset functionality
- Workout templates and favorites
- Social sharing of workouts
- User preferences (default sport, units)
- Advanced workout search and filters

## Medium-Term Features (Month 4-6)
- Workout analytics and insights
- Training plan generation
- Integration with other platforms (Strava, TrainingPeaks)
- Mobile app (React Native)
- Team/coach features
- API for third-party developers

## Long-Term Vision (6+ Months)
- AI-powered workout recommendations
- Performance prediction models
- Community features (share, like, comment)
- Premium subscription tier
- White-label solution for coaches
- Multi-language support

---

# Risk Management

## Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Garmin API changes | High | Monitor unofficial API, have fallback, build abstractions |
| Database performance | Medium | Implement indexing, query optimization, connection pooling |
| API rate limits (Gemini) | Medium | Implement caching, user rate limits, fallback to Claude |
| Security breach | High | Follow security checklist, regular audits, encryption |

## Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Low user adoption | Medium | Focus on UX, gather feedback, iterate quickly |
| Hosting costs | Low | Start with free tiers, optimize before scaling |
| Competition | Low | Unique AI parsing feature, better UX |
| Legal issues | Medium | Clear ToS, privacy policy, data handling compliance |

---

# Success Metrics

## Launch Metrics (Week 1)
- Application deployed and accessible
- Zero critical bugs
- <2s page load time
- 99% uptime

## Growth Metrics (Month 1)
- 50+ registered users
- 200+ workouts created
- <5% error rate
- Positive user feedback

## Quality Metrics (Ongoing)
- >95% test coverage
- <1% API error rate
- <500ms average API response
- >99% uptime

---

# Resources & Documentation

## Development Resources
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Garth Library:** https://github.com/matin/garth

## Security Resources
- **OWASP Top 10:** https://owasp.org/Top10/
- **JWT Best Practices:** https://tools.ietf.org/html/rfc8725
- **Python Security:** https://python.readthedocs.io/en/stable/library/security_warnings.html

## Deployment Guides
- **Railway:** https://docs.railway.app
- **Render:** https://render.com/docs
- **Docker:** https://docs.docker.com

---

# Quick Start Commands

## Initial Setup
```bash
# Generate security keys
openssl rand -hex 32  # SECRET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Create database
createdb garmin_workouts

# Install backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Install frontend
cd frontend
npm install
```

## Development
```bash
# Run backend (terminal 1)
cd backend && uvicorn app.main:app --reload

# Run frontend (terminal 2)
cd frontend && npm run dev
```

## Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## Deployment
```bash
# Build Docker images
docker-compose build

# Deploy to Railway
railway up

# Deploy to Render
git push render main
```

---

# Next Steps

## Immediate Actions (Week 1)
1. ✅ Review this implementation plan
2. ⏳ Generate security keys (SECRET_KEY, ENCRYPTION_KEY)
3. ⏳ Set up PostgreSQL database
4. ⏳ Create backend and frontend folder structure
5. ⏳ Install dependencies
6. ⏳ Configure environment variables

## This Week
- Complete Phase 1 setup
- Start Phase 2 backend development
- Create first API endpoints

## This Month
- Complete backend API (Phase 2)
- Build frontend UI (Phase 3)
- Basic deployment

## Ready to Begin?
**Start with Phase 1, Task 1: Generate your security keys!**

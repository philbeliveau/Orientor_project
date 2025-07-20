# Orientor Platform - Deployment Architecture

## Overview

Your Orientor project uses a **microservices architecture** with separate deployments for frontend and backend that communicate via HTTP APIs and Vercel proxy rewrites.

## Architecture Diagram

```
[Vercel Frontend] ←→ [Proxy Rewrites] ←→ [Railway Backend] ←→ [Database]
```

## Frontend Deployment (Vercel)

- **Platform**: Vercel
- **Framework**: Next.js 13.5.11
- **Domain**: Auto-generated Vercel URL
- **Build Command**: `npm run build` in `/frontend` directory
- **Output Directory**: `frontend/.next`
- **Environment Variables**: 
  - `NEXT_PUBLIC_API_URL`: `/api` (relative)
  - `NEXT_PUBLIC_BACKEND_URL`: `https://orientor-backend-production-7c13.up.railway.app`

## Backend Deployment (Railway)

- **Platform**: Railway
- **Framework**: FastAPI + Uvicorn
- **Domain**: `https://orientor-backend-production-7c13.up.railway.app`
- **Runtime**: Python 3.11
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Build Configuration**: 
  - Builder: Nixpacks
  - Python packages: FastAPI, Uvicorn, Python-multipart

## Communication Layer

### Vercel Proxy Rewrites (Key Component)

The communication between frontend and backend is handled through Vercel's proxy rewrite system:

```json
{
  "rewrites": [
    {
      "source": "/api/tests/(.*)",
      "destination": "https://orientor-backend-production-7c13.up.railway.app/api/tests/$1"
    },
    {
      "source": "/api/(.*)", 
      "destination": "https://orientor-backend-production-7c13.up.railway.app/$1"
    }
  ]
}
```

### Frontend API Configuration

```typescript
// Frontend API setup
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
// In production: API_URL = "/api"

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Example API call
const response = await api.get(`/careers/recommendations?limit=${limit}`);
// This becomes: GET /api/careers/recommendations?limit=30
```

### Request Flow

1. **Frontend Request**: `fetch('/api/careers/recommendations')`
2. **Vercel Proxy**: Rewrites to Railway backend URL
3. **Railway Backend**: Receives at `https://orientor-backend-production-7c13.up.railway.app/careers/recommendations`
4. **Railway Response**: Returns JSON data
5. **Vercel Proxy**: Forwards response back to frontend
6. **Frontend**: Receives and processes data

## Security & Authentication

### CORS Configuration

Backend CORS setup allows cross-origin requests:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication Flow

```typescript
// JWT token storage and transmission
const token = localStorage.getItem('access_token');

// Axios interceptor adds authentication to all requests
api.interceptors.request.use((config) => {
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Development vs Production

### Local Development
- **Frontend**: `localhost:3000` 
- **Backend**: `localhost:8000`
- **Communication**: Direct HTTP calls

### Production
- **Frontend**: `https://[project].vercel.app`
- **Backend**: `https://orientor-backend-production-7c13.up.railway.app`
- **Communication**: Proxied through Vercel rewrites

## Architecture Benefits

1. **Independent Scaling**: Frontend and backend can scale separately based on demand
2. **Performance Optimization**: 
   - Vercel's global edge network for frontend delivery
   - Railway's optimized containers for backend processing
3. **Development Efficiency**: Teams can develop frontend and backend independently
4. **Security**: Backend API is only accessible through defined proxy routes
5. **SEO & Performance**: Next.js provides server-side rendering via Vercel's infrastructure
6. **Cost Optimization**: Pay-per-use scaling on both platforms

## Key Technical Components

### Frontend Technologies
- **Next.js 13.5.11**: React framework with SSR
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client with interceptors
- **React Query**: Data fetching and caching

### Backend Technologies
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations
- **JWT Authentication**: Token-based auth
- **PostgreSQL**: Primary database

### Infrastructure
- **Vercel**: Frontend hosting with edge network
- **Railway**: Backend hosting with container deployment
- **Proxy Rewrites**: Seamless API communication
- **Environment Variables**: Configuration management

## Monitoring & Deployment

### Deployment Process
1. **Frontend**: Git push → Vercel auto-deployment
2. **Backend**: Git push → Railway auto-deployment
3. **Database**: Managed PostgreSQL on Railway

### Environment Management
- **Development**: Local environment with Docker/direct Python
- **Production**: Vercel + Railway with environment-specific configs

---

## Summary

The Orientor platform uses a modern, distributed architecture that separates concerns while maintaining seamless user experience. The Vercel proxy rewrite system is the key innovation that makes this distributed architecture appear as a single domain to browsers, avoiding CORS complexities while enabling independent scaling and deployment of frontend and backend services.

This architecture provides excellent developer experience, performance, and scalability while maintaining security and cost efficiency.
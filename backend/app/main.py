"""FastAPI application entry point with CORS, security headers, and all routers."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

app = FastAPI(
    title="VotoClaro v3",
    description="Strategic voting app for Peru 2026 elections",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware stack (applied bottom-to-top) ---

# 1. Security headers on every response
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate limiting on sensitive endpoints
app.add_middleware(RateLimitMiddleware)

# 3. CORS — only allow configured origins, restrict methods & headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Include all API routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "app": "VotoClaro v3",
        "version": "3.0.0",
        "description": "Vota inteligente. Peru 2026.",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

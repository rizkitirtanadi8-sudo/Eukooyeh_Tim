"""
Main FastAPI application.
Clean, modular, dan production-ready.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import get_settings
from app.api.routes import products, marketplaces, enrichment, uploads, trends, shopify
from app.api.routes import settings as settings_routes
from app.api.endpoints import mock_marketplaces, trend_analysis, test_google_search, marketplaces as marketplaces_endpoints


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager untuk startup dan shutdown events.
    """
    # Startup
    settings = get_settings()
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    print("=" * 50)
    print(f"🚀 {settings.api_title} v{settings.api_version}")
    print(f"📁 Upload directory: {settings.upload_dir}")
    print(f"🤖 AI Model: {settings.openai_model_name}")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("👋 Shutting down gracefully...")


def create_application() -> FastAPI:
    """
    Application factory untuk create FastAPI instance.
    Menggunakan best practices untuk production deployment.
    """
    settings = get_settings()
    
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers (NO USER AUTH - Open Source Mode)
    app.include_router(settings_routes.router, prefix="/api/v1")
    app.include_router(shopify.router, prefix="/api/v1")
    app.include_router(products.router, prefix="/api/v1")
    app.include_router(enrichment.router, prefix="/api/v1")
    app.include_router(marketplaces.router, prefix="/api/v1")
    app.include_router(trends.router, prefix="/api/v1")
    app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
    
    # New endpoints
    app.include_router(mock_marketplaces.router, prefix="/api/v1")
    app.include_router(trend_analysis.router, prefix="/api/v1")
    app.include_router(test_google_search.router, prefix="/api/v1")
    app.include_router(marketplaces_endpoints.router, prefix="/api/v1")
    
    # Serve uploaded files statically
    if os.path.exists(settings.upload_dir):
        app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "service": settings.api_title,
            "version": settings.api_version,
            "status": "running",
            "docs": "/docs",
            "health": "/api/v1/products/health"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "path": str(request.url)
            }
        )
    
    return app


# Create app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

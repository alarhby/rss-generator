"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import feeds, rss


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up RSS Generator application...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down RSS Generator application...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RSS Generator - Convert any HTML site to RSS feed",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(feeds.router)
app.include_router(rss.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name}
    )


@app.get("/create", response_class=HTMLResponse)
async def create_feed_page(request: Request):
    """Create feed page."""
    return templates.TemplateResponse(
        request=request,
        name="create_feed.html",
        context={"app_name": settings.app_name}
    )


@app.get("/manage", response_class=HTMLResponse)
async def manage_feeds_page(request: Request):
    """Manage feeds page."""
    return templates.TemplateResponse(
        request=request,
        name="manage_feeds.html",
        context={"app_name": settings.app_name}
    )


@app.get("/configure/{feed_id}", response_class=HTMLResponse)
async def configure_feed_page(request: Request, feed_id: str):
    """Configure feed page."""
    return templates.TemplateResponse(
        request=request,
        name="configure_feed.html",
        context={"app_name": settings.app_name, "feed_id": feed_id}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

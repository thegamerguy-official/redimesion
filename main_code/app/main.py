"""
REDIMENSION API v2 — Application Entry Point.

FastAPI application with Clean Architecture, 3D Bin Packing engine,
and PostgreSQL persistence via Prisma ORM.
"""

import contextlib
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import pack_router
from app.core.database import connect_db, disconnect_db
from app.core.exceptions import setup_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    logger.info("REDIMENSION API v2 starting up...")
    connect_db()
    yield
    logger.info("REDIMENSION API v2 shutting down...")
    disconnect_db()


app = FastAPI(
    title="REDIMENSION API v2",
    description="Motor de Cálculo 3D Bin Packing con Clean Architecture y Alto Rendimiento",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_exception_handlers(app)

app.include_router(pack_router.router, prefix="/api/v1", tags=["Packer"])


@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint."""
    return {"message": "REDIMENSION Backend v2 is running."}

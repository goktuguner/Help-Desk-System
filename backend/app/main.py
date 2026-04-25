"""FastAPI application entry point with lifespan, CORS, and router registration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import auth_router, categories, comments, tickets, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Help Desk Ticketing System",
    description="REST API for managing support tickets, comments, and users.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Tkinter client and any localhost origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router.router)
app.include_router(tickets.router)
app.include_router(comments.router)
app.include_router(categories.router)
app.include_router(users.router)


@app.get("/", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "helpdesk-api"}

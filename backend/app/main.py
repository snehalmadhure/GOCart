"""FastAPI entry point for the GOCart backend."""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers.alerts import router as alerts_router
from app.routers.lists import router as lists_router
from app.routers.pantry import router as pantry_router
from app.routers.purchases import import_router, router as purchases_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create development tables before the application accepts requests."""

    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="GOCart API",
    version="0.1.0",
    description="Purchase logging, pantry state, and restock planning API.",
    lifespan=lifespan,
)
app.include_router(purchases_router)
app.include_router(import_router)
app.include_router(pantry_router)
app.include_router(alerts_router)
app.include_router(lists_router)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "GOCART_CORS_ORIGINS",
        "http://localhost:5173,https://gocart-kashish-43dd.vercel.app",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Return service health for local development and deployment checks."""

    return {"status": "ok"}

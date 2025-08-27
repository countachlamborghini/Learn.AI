from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Global Brain API",
        version="0.1.0",
        description="Backend API for Global Brain — Student Edition (MVP)",
    )

    # CORS (allow all origins for now; lock down in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/v1")

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
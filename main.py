import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import chat_router, pages_router
from core.motor_factory import crear_motor_activo
from core.server import obtener_puerto_disponible

RUTA_STATIC = Path(__file__).resolve().parent / "frontend" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.motor_activo = crear_motor_activo()
    yield


def crear_app() -> FastAPI:
    app = FastAPI(title="Tutor Mandarín RAG API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory=str(RUTA_STATIC)), name="static")
    app.include_router(pages_router)
    app.include_router(chat_router)
    return app


app = crear_app()


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    puerto_preferido = int(os.getenv("PORT", "8000"))
    puerto = obtener_puerto_disponible(puerto_preferido)

    if puerto != puerto_preferido:
        print(f"-> Puerto {puerto_preferido} ocupado. Iniciando en {puerto}.")

    uvicorn.run(app, host=host, port=puerto)

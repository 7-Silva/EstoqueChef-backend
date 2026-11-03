from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__, models  # noqa: F401  (importar os models registra as tabelas)
from .config import settings
from .db import Base, engine
from .routes import auth, entradas, ingredientes, saidas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Simples para portfólio. Em produção: migrações com Alembic.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="EstoqueChef API",
    version=__version__,
    description="Controle de estoque para restaurantes e confeitarias.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origens_cors,
    allow_methods=["*"],
    allow_headers=["*"],
)

for roteador in (auth.router, ingredientes.router, entradas.router, saidas.router):
    app.include_router(roteador)


@app.get("/health", tags=["infra"])
def health():
    return {"status": "ok"}

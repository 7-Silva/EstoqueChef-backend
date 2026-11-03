from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


def criar_engine(url: str):
    # check_same_thread só existe no SQLite; o FastAPI usa threads diferentes.
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=args, pool_pre_ping=True)


engine = criar_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session():
    """Dependência do FastAPI: uma sessão por requisição."""
    with SessionLocal() as sessao:
        yield sessao

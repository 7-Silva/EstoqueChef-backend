"""Hash de senha (bcrypt) e tokens JWT (access + refresh)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings

ALGORITMO = "HS256"


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, hash_: str) -> bool:
    return bcrypt.checkpw(senha.encode(), hash_.encode())


def _criar_token(username: str, tipo: str, validade: timedelta) -> str:
    agora = datetime.now(timezone.utc)
    payload = {"sub": username, "type": tipo, "iat": agora, "exp": agora + validade}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITMO)


def criar_access_token(username: str) -> str:
    return _criar_token(username, "access", timedelta(minutes=settings.access_token_minutes))


def criar_refresh_token(username: str) -> str:
    return _criar_token(username, "refresh", timedelta(days=settings.refresh_token_days))


def ler_token(token: str, tipo: str) -> str | None:
    """Devolve o username se o token for válido e do tipo esperado."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != tipo:
        return None
    return payload.get("sub")

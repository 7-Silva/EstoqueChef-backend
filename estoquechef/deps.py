from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_session
from .models import Usuario
from .security import ler_token

oauth2 = OAuth2PasswordBearer(tokenUrl="token")


def usuario_logado(token: str = Depends(oauth2), sessao: Session = Depends(get_session)) -> Usuario:
    erro = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado", headers={"WWW-Authenticate": "Bearer"}
    )
    username = ler_token(token, "access")
    if not username:
        raise erro
    usuario = sessao.scalar(select(Usuario).where(Usuario.username == username))
    if not usuario:
        raise erro
    return usuario

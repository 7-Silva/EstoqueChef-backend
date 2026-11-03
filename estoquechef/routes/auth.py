from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..db import get_session
from ..deps import usuario_logado
from ..models import Usuario
from ..schemas import RefreshIn, TokenOut, UsuarioCreate, UsuarioOut
from ..security import criar_access_token, criar_refresh_token, gerar_hash, ler_token, verificar_senha

router = APIRouter(tags=["auth"])


def _tokens(username: str) -> TokenOut:
    return TokenOut(access_token=criar_access_token(username), refresh_token=criar_refresh_token(username))


@router.post("/token", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), sessao: Session = Depends(get_session)):
    """Login OAuth2 (form `username`/`password`, não JSON)."""
    usuario = sessao.scalar(select(Usuario).where(Usuario.username == form.username))
    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário ou senha incorretos.")
    return _tokens(usuario.username)


@router.post("/refresh_token", response_model=TokenOut)
def renovar(dados: RefreshIn, sessao: Session = Depends(get_session)):
    username = ler_token(dados.refresh_token, "refresh")
    if not username or not sessao.scalar(select(Usuario.id).where(Usuario.username == username)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido ou expirado.")
    return _tokens(username)


@router.post("/user/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: UsuarioCreate, sessao: Session = Depends(get_session)):
    existe = sessao.scalar(
        select(Usuario).where(or_(Usuario.username == dados.username, Usuario.email == dados.email))
    )
    if existe:
        raise HTTPException(status.HTTP_409_CONFLICT, "Usuário ou email já cadastrado.")
    usuario = Usuario(username=dados.username, email=dados.email, senha_hash=gerar_hash(dados.password))
    sessao.add(usuario)
    sessao.commit()
    return usuario


@router.get("/user/{username}/", response_model=UsuarioOut)
def ver_usuario(username: str, atual: Usuario = Depends(usuario_logado)):
    if username != atual.username:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Você só pode ver o seu próprio perfil.")
    return atual

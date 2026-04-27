"""
auth.py  ─  JWT autenticación y utilidades de seguridad
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
import models

# ── Configuración ──────────────────────────────────────────────────────────────
# ⚠️  En producción cambia SECRET_KEY por una cadena aleatoria larga
SECRET_KEY  = "cambia-esto-por-una-clave-secreta-larga-y-aleatoria"
ALGORITHM   = "HS256"
EXPIRACION_MINUTOS = 60 * 24  # 24 horas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Passwords ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# ── JWT ────────────────────────────────────────────────────────────────────────

def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expira  = datetime.utcnow() + (expires_delta or timedelta(minutes=EXPIRACION_MINUTOS))
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """Dependencia: extrae y valida el usuario del token JWT."""
    credenciales_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credenciales_error
    except JWTError:
        raise credenciales_error

    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise credenciales_error
    return usuario
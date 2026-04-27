"""
models.py  ─  Tablas de la base de datos SQLite
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id         = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, index=True, nullable=False)
    password   = Column(String(255), nullable=False)
    creado_en  = Column(DateTime, server_default=func.now())

    busquedas  = relationship("Busqueda", back_populates="usuario")


class Busqueda(Base):
    __tablename__ = "busquedas"

    id          = Column(Integer, primary_key=True, index=True)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    producto    = Column(String(255), nullable=False)
    tienda      = Column(String(100), nullable=False)
    url         = Column(Text, nullable=False)
    total       = Column(Integer, default=0)
    creada_en   = Column(DateTime, server_default=func.now())

    usuario     = relationship("Usuario", back_populates="busquedas")
    productos   = relationship("Producto", back_populates="busqueda", cascade="all, delete-orphan")


class Producto(Base):
    __tablename__ = "productos"

    id           = Column(Integer, primary_key=True, index=True)
    busqueda_id  = Column(Integer, ForeignKey("busquedas.id"), nullable=False)
    tienda       = Column(String(100), nullable=False)
    titulo       = Column(Text, nullable=False)
    precio_texto = Column(String(50))
    precio       = Column(Float)
    creado_en    = Column(DateTime, server_default=func.now())

    busqueda     = relationship("Busqueda", back_populates="productos")
"""
schemas.py  ─  Modelos Pydantic para validación y documentación
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Auth ───────────────────────────────────────────────────────────────────────

class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Juan Pérez"])
    email:  EmailStr = Field(..., examples=["juan@email.com"])
    password: str = Field(..., min_length=6, examples=["mipassword123"])


class UsuarioLogin(BaseModel):
    email:    EmailStr = Field(..., examples=["juan@email.com"])
    password: str      = Field(..., examples=["mipassword123"])


class UsuarioRespuesta(BaseModel):
    id:        int
    nombre:    str
    email:     str
    creado_en: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── Scraper ────────────────────────────────────────────────────────────────────

TIENDAS_VALIDAS = ["Mercado Libre", "Amazon", "AliExpress", "Shein", "Temu"]

class BusquedaRequest(BaseModel):
    producto: str  = Field(..., min_length=2, max_length=200, examples=["laptop gamer"])
    tienda:   str  = Field(..., examples=["Mercado Libre"])

    class Config:
        json_schema_extra = {
            "example": {
                "producto": "laptop gamer",
                "tienda": "Mercado Libre"
            }
        }


class ProductoRespuesta(BaseModel):
    id:           int
    tienda:       str
    titulo:       str
    precio_texto: Optional[str]
    precio:       Optional[float]
    creado_en:    datetime

    class Config:
        from_attributes = True


class BusquedaRespuesta(BaseModel):
    id:         int
    producto:   str
    tienda:     str
    url:        str
    total:      int
    creada_en:  datetime
    productos:  list[ProductoRespuesta] = []

    class Config:
        from_attributes = True


class BusquedaResumen(BaseModel):
    id:        int
    producto:  str
    tienda:    str
    total:     int
    creada_en: datetime

    class Config:
        from_attributes = True


# ── Comparador ─────────────────────────────────────────────────────────────────

class EstadisticaTienda(BaseModel):
    tienda:          str
    total_productos: int
    precio_promedio: Optional[float]
    precio_mediana:  Optional[float]
    precio_minimo:   Optional[float]
    precio_maximo:   Optional[float]


class ComparacionRespuesta(BaseModel):
    producto:          str
    tiendas_comparadas: int
    estadisticas:      list[EstadisticaTienda]
    tienda_mas_barata: Optional[str]
    tienda_mas_cara:   Optional[str]
    diferencia_pct:    Optional[float]
    top_baratos:       list[ProductoRespuesta]
    top_caros:         list[ProductoRespuesta]
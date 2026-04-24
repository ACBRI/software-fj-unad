"""Núcleo del sistema: entidad base, excepciones y logger."""

from src.core.entidad_base import EntidadBase
from src.core.excepciones import (
    SoftwareFJError,
    DatosInvalidosError,
    ClienteInvalidoError,
    ServicioNoDisponibleError,
    ReservaInvalidaError,
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
)
from src.core.logger import obtener_logger

__all__ = [
    "EntidadBase",
    "SoftwareFJError",
    "DatosInvalidosError",
    "ClienteInvalidoError",
    "ServicioNoDisponibleError",
    "ReservaInvalidaError",
    "CalculoInconsistenteError",
    "OperacionNoPermitidaError",
    "obtener_logger",
]

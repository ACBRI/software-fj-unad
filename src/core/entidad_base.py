"""
Clase abstracta raíz de todas las entidades del dominio.

Define contrato mínimo (identificador, descripción, validación) y
comportamiento común (timestamp de creación, representación legible,
igualdad por identificador). Toda entidad persistible del sistema
—Cliente, Servicio, Reserva— desciende de EntidadBase.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4

from src.core.excepciones import DatosInvalidosError


class EntidadBase(ABC):
    """Contrato común para todas las entidades de Software FJ."""

    def __init__(self, identificador: str | None = None) -> None:
        if identificador is not None and not identificador.strip():
            raise DatosInvalidosError(
                "El identificador no puede ser una cadena vacía."
            )
        self._identificador: str = identificador or uuid4().hex[:12]
        self._creado_en: datetime = datetime.now()

    @property
    def identificador(self) -> str:
        return self._identificador

    @property
    def creado_en(self) -> datetime:
        return self._creado_en

    @abstractmethod
    def describir(self) -> str:
        """Descripción legible de la entidad (para logs y UI)."""

    @abstractmethod
    def validar(self) -> None:
        """Valida el estado interno. Debe lanzar DatosInvalidosError si falla."""

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, EntidadBase):
            return NotImplemented
        return (
            type(self) is type(otro)
            and self._identificador == otro._identificador
        )

    def __hash__(self) -> int:
        return hash((type(self), self._identificador))

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self._identificador}>"

"""
AlquilerEquipo — STUB pendiente de implementación completa.

Responsable: Hernán David Olaya Martínez (issue #3)
"""

from __future__ import annotations

from src.core.excepciones import DatosInvalidosError
from src.modelos.servicio import Servicio


class AlquilerEquipo(Servicio):
    """Servicio: alquiler de equipo tecnológico."""

    def __init__(self, nombre: str, tarifa_base: float, tipo_equipo: str) -> None:
        super().__init__(nombre, tarifa_base)
        if not tipo_equipo:
            raise DatosInvalidosError("Tipo de equipo no puede estar vacío.")
        self._tipo_equipo = tipo_equipo

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    def describir(self) -> str:
        return (
            f"Alquiler de {self._tipo_equipo} ({self.nombre}) — "
            f"${self.tarifa_base:,.0f}/hora"
        )

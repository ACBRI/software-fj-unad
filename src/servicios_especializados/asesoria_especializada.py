"""
AsesoriaEspecializada — STUB pendiente de implementación completa.

Responsable: Hernán David Olaya Martínez (issue #3)
"""

from __future__ import annotations

from src.core.excepciones import DatosInvalidosError
from src.modelos.servicio import Servicio


class AsesoriaEspecializada(Servicio):
    """Servicio: asesoría profesional especializada."""

    def __init__(self, nombre: str, tarifa_base: float, area: str) -> None:
        super().__init__(nombre, tarifa_base)
        if not area:
            raise DatosInvalidosError("Área de asesoría no puede estar vacía.")
        self._area = area

    @property
    def area(self) -> str:
        return self._area

    def describir(self) -> str:
        return (
            f"Asesoría en {self._area} ({self.nombre}) — "
            f"${self.tarifa_base:,.0f}/hora"
        )

    def calcular_costo(
        self,
        horas: float,
        *,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ) -> float:
        if horas >= 10 and descuento == 0.0:
            descuento = 0.10
        return super().calcular_costo(horas, impuesto=impuesto, descuento=descuento)

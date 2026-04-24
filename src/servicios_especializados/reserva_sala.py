"""
ReservaSala — STUB pendiente de implementación completa.

Responsable: Hernán David Olaya Martínez (issue #3)

Polimorfismo: sobreescribe describir() con formato específico de salas
y puede extender calcular_costo() incorporando un recargo por capacidad.
"""

from __future__ import annotations

from src.core.excepciones import DatosInvalidosError
from src.modelos.servicio import Servicio


class ReservaSala(Servicio):
    """Servicio: reserva de sala de reuniones."""

    def __init__(self, nombre: str, tarifa_base: float, capacidad: int) -> None:
        super().__init__(nombre, tarifa_base)
        if capacidad <= 0:
            raise DatosInvalidosError(
                f"Capacidad debe ser > 0 (recibido: {capacidad})."
            )
        self._capacidad = capacidad

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def describir(self) -> str:
        return (
            f"Sala '{self.nombre}' — capacidad {self._capacidad} personas — "
            f"${self.tarifa_base:,.0f}/hora"
        )

    def calcular_costo(
        self,
        horas: float,
        *,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ) -> float:
        base = super().calcular_costo(horas, impuesto=impuesto, descuento=descuento)
        recargo_capacidad = 1 + (self._capacidad / 100)
        return round(base * recargo_capacidad, 2)

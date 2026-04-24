"""
Clase abstracta Servicio — STUB pendiente de implementación.

Responsable: Hernán David Olaya Martínez (issue #3)

Contrato mínimo esperado:
    - Abstracta: hereda de EntidadBase
    - Atributos comunes: nombre, tarifa_base, activo
    - Métodos abstractos que las subclases deben implementar:
        * calcular_costo(horas: float) -> float
        * describir() -> str
    - Método sobrecargado (vía argumentos opcionales):
        calcular_costo(horas, *, impuesto=0.19, descuento=0.0)
    - Validaciones: tarifa_base > 0, horas > 0
"""

from __future__ import annotations

from abc import abstractmethod

from src.core.entidad_base import EntidadBase
from src.core.excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ServicioNoDisponibleError,
)


class Servicio(EntidadBase):
    """Placeholder — sustituir por la implementación de Hernán David."""

    def __init__(self, nombre: str, tarifa_base: float) -> None:
        super().__init__()
        if not nombre or len(nombre.strip()) < 3:
            raise DatosInvalidosError(f"Nombre de servicio inválido: {nombre!r}.")
        if tarifa_base <= 0:
            raise DatosInvalidosError(
                f"Tarifa base debe ser > 0 (recibido: {tarifa_base})."
            )
        self._nombre = nombre
        self._tarifa_base = tarifa_base
        self._activo = True

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False

    def verificar_disponibilidad(self) -> None:
        if not self._activo:
            raise ServicioNoDisponibleError(
                f"Servicio {self._nombre!r} está desactivado."
            )

    def calcular_costo(
        self,
        horas: float,
        *,
        impuesto: float = 0.19,
        descuento: float = 0.0,
    ) -> float:
        """Cálculo base con parámetros opcionales (sobrecarga por kwargs)."""
        if horas <= 0:
            raise DatosInvalidosError(f"Horas debe ser > 0 (recibido: {horas}).")
        if not 0 <= descuento <= 1:
            raise DatosInvalidosError(
                f"Descuento debe estar en [0, 1] (recibido: {descuento})."
            )
        bruto = self._tarifa_base * horas
        neto = bruto * (1 - descuento) * (1 + impuesto)
        if neto < 0:
            raise CalculoInconsistenteError(
                f"Costo calculado negativo ({neto}) para {self._nombre!r}."
            )
        return round(neto, 2)

    @abstractmethod
    def describir(self) -> str: ...

    def validar(self) -> None:
        if self._tarifa_base <= 0:
            raise DatosInvalidosError("Tarifa base inválida.")

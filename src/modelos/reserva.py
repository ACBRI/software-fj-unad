"""
Clase Reserva — STUB pendiente de implementación.

Responsable: Wilmer García Ochoa (issue #4)

Contrato mínimo esperado:
    - Integra Cliente + Servicio + duración (horas) + estado
    - Estados: PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA
    - Métodos:
        * confirmar()    — solo si está PENDIENTE
        * cancelar()     — desde cualquier estado salvo PROCESADA
        * procesar()     — solo si está CONFIRMADA, lanza cálculo de costo
    - Métodos sobrecargados:
        * total_con_descuento(porcentaje)
        * total_con_impuesto_personalizado(impuesto)
"""

from __future__ import annotations

from enum import Enum

from src.core.entidad_base import EntidadBase
from src.core.excepciones import (
    OperacionNoPermitidaError,
    ReservaInvalidaError,
)
from src.modelos.cliente import Cliente
from src.modelos.servicio import Servicio


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    PROCESADA = "procesada"


class Reserva(EntidadBase):
    """Placeholder — sustituir por la implementación de Wilmer."""

    def __init__(self, cliente: Cliente, servicio: Servicio, horas: float) -> None:
        super().__init__()
        if horas <= 0:
            raise ReservaInvalidaError(
                f"Duración inválida: {horas} horas (debe ser > 0)."
            )
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = EstadoReserva.PENDIENTE
        self._costo_final: float | None = None

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_final(self) -> float | None:
        return self._costo_final

    def confirmar(self) -> None:
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado.value}."
            )
        self._servicio.verificar_disponibilidad()
        self._estado = EstadoReserva.CONFIRMADA

    def cancelar(self) -> None:
        if self._estado is EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError(
                "No se puede cancelar una reserva ya procesada."
            )
        self._estado = EstadoReserva.CANCELADA

    def procesar(self) -> float:
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas (estado actual: {self._estado.value})."
            )
        self._costo_final = self._servicio.calcular_costo(self._horas)
        self._estado = EstadoReserva.PROCESADA
        return self._costo_final

    def describir(self) -> str:
        return (
            f"Reserva #{self.identificador[:6]} — {self._cliente.nombre} → "
            f"{self._servicio.nombre} ({self._horas}h) — {self._estado.value}"
        )

    def validar(self) -> None:
        if self._horas <= 0:
            raise ReservaInvalidaError("Duración debe ser > 0.")

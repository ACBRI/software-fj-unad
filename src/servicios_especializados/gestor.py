"""
GestorSistema — orquestador central de Software FJ.

Mantiene las listas internas de clientes, servicios y reservas, y es el
único punto por el que se crean o cancelan operaciones de negocio.
Todas las operaciones se envuelven en try/except/else/finally para
garantizar que la aplicación nunca se detenga y todo quede registrado
en el log.
"""

from __future__ import annotations

from typing import Iterable

from src.core.excepciones import (
    ClienteInvalidoError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from src.core.logger import obtener_logger
from src.modelos.cliente import Cliente
from src.modelos.reserva import EstadoReserva, Reserva
from src.modelos.servicio import Servicio

_log = obtener_logger(__name__)


class GestorSistema:
    """Fachada de operaciones del dominio."""

    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        """Registra un cliente validando duplicidad por cédula."""
        try:
            if any(c.cedula == cliente.cedula for c in self._clientes):
                raise ClienteInvalidoError(
                    f"Ya existe un cliente con cédula {cliente.cedula}."
                )
            self._clientes.append(cliente)
        except SoftwareFJError as error:
            _log.error("Fallo al registrar cliente: %s", error)
            raise
        else:
            _log.info("Cliente registrado: %s", cliente.describir())
            return cliente
        finally:
            _log.debug("Total de clientes registrados: %d", len(self._clientes))

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        try:
            servicio.verificar_disponibilidad()
            self._servicios.append(servicio)
        except SoftwareFJError as error:
            _log.error("Fallo al registrar servicio: %s", error)
            raise
        else:
            _log.info("Servicio registrado: %s", servicio.describir())
            return servicio

    def crear_reserva(
        self, cliente: Cliente, servicio: Servicio, horas: float
    ) -> Reserva:
        """Crea una reserva pendiente tras validar datos de entrada."""
        try:
            if cliente not in self._clientes:
                raise ClienteInvalidoError(
                    f"El cliente {cliente.cedula} no está registrado."
                )
            if servicio not in self._servicios:
                raise ServicioNoDisponibleError(
                    f"El servicio {servicio.nombre!r} no está registrado."
                )
            servicio.verificar_disponibilidad()
            reserva = Reserva(cliente, servicio, horas)
        except SoftwareFJError as error:
            _log.error("No se pudo crear la reserva: %s", error)
            raise
        except Exception as exc:
            raise ReservaInvalidaError(
                "Error inesperado creando la reserva."
            ) from exc
        else:
            self._reservas.append(reserva)
            _log.info("Reserva creada: %s", reserva.describir())
            return reserva

    def procesar_reserva(self, reserva: Reserva) -> float:
        """Confirma + procesa una reserva, devolviendo el costo final."""
        try:
            if reserva.estado is EstadoReserva.PENDIENTE:
                reserva.confirmar()
            costo = reserva.procesar()
        except OperacionNoPermitidaError as error:
            _log.warning(
                "Operación no permitida sobre reserva %s: %s",
                reserva.identificador[:6],
                error,
            )
            raise
        except SoftwareFJError as error:
            _log.error("Fallo procesando reserva: %s", error)
            raise
        else:
            _log.info(
                "Reserva %s procesada: costo final $%s",
                reserva.identificador[:6],
                f"{costo:,.2f}",
            )
            return costo
        finally:
            _log.debug("Estado final de la reserva: %s", reserva.estado.value)

    def resumen(self) -> str:
        procesadas = sum(
            1 for r in self._reservas if r.estado is EstadoReserva.PROCESADA
        )
        canceladas = sum(
            1 for r in self._reservas if r.estado is EstadoReserva.CANCELADA
        )
        return (
            f"Clientes: {len(self._clientes)} | Servicios: {len(self._servicios)} | "
            f"Reservas totales: {len(self._reservas)} "
            f"(procesadas={procesadas}, canceladas={canceladas})"
        )

    def iterar_reservas(self) -> Iterable[Reserva]:
        return iter(self._reservas)

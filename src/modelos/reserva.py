"""
Clase Reserva del sistema Software FJ — máquina de estados, sobrecarga,
manejo avanzado de excepciones.

Implementación original: Hernán David Olaya Martínez (issue #4, rama feat/reservas).
Integración con el núcleo del sistema: Andrés Camilo Briñez Núñez.

CONCEPTOS APLICADOS:
    - Encapsulación: atributos privados con properties.
    - Sobrecarga: procesar_pago() con variantes de parámetros.
    - Manejo avanzado de excepciones (try/except/else/finally + encadenamiento).
    - Logging centralizado vía src.core.logger.
    - Compatibilidad con la interfaz simplificada del GestorSistema
      (procesar() = confirmar + procesar_pago + completar).

Nota arquitectural: la clase `Cliente` interna que existía en el archivo
original (Reservas.py) fue eliminada — el módulo ahora importa el `Cliente`
oficial de `src.modelos.cliente` (módulo de Jhon Alejandro). De igual modo,
el `GestorReservas` original quedó subsumido en el `GestorSistema` del núcleo.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from src.core.entidad_base import EntidadBase
from src.core.excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from src.core.logger import obtener_logger
from src.modelos.cliente import Cliente
from src.modelos.servicio import Servicio

_log = obtener_logger(__name__)


class EstadoReserva(Enum):
    """
    Estados válidos de una Reserva.

    Ciclo de vida:
        PENDIENTE -> CONFIRMADA -> PROCESADA -> COMPLETADA
                  -> CANCELADA (desde PENDIENTE o CONFIRMADA)
    """

    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    PROCESADA = "procesada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class Reserva(EntidadBase):
    """
    Reserva que integra Cliente + Servicio + duración + estado + pagos.

    Sobrecarga: `procesar_pago()` acepta distintas combinaciones de
    parámetros (monto, descuento_extra, metodo_pago, cuotas).
    """

    TRANSICIONES_VALIDAS = {
        EstadoReserva.PENDIENTE:  {EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA},
        EstadoReserva.CONFIRMADA: {EstadoReserva.PROCESADA, EstadoReserva.CANCELADA},
        EstadoReserva.PROCESADA:  {EstadoReserva.COMPLETADA},
        EstadoReserva.COMPLETADA: set(),
        EstadoReserva.CANCELADA:  set(),
    }

    CARGO_CANCELACION = 0.10  # 10% por cancelación tardía (estaba CONFIRMADA)

    def __init__(self, cliente: Cliente, servicio: Servicio,
                 horas: float, *, reserva_id: str | None = None,
                 personas: int = 1):
        """
        Constructor compatible con dos firmas:
            Reserva(cliente, servicio, horas)                           # uso del gestor
            Reserva(cliente, servicio, horas, reserva_id=..., personas=)  # API rica
        """
        try:
            super().__init__(identificador=reserva_id)

            if not isinstance(cliente, Cliente):
                raise ReservaInvalidaError("Se esperaba un objeto Cliente válido.")
            if not isinstance(servicio, Servicio):
                raise ReservaInvalidaError("Se esperaba un objeto Servicio válido.")
            if not isinstance(horas, (int, float)) or horas <= 0:
                raise ReservaInvalidaError(
                    f"Duración inválida: {horas} horas (debe ser un número > 0)."
                )

            # Si el servicio expone validar_parametros (jerarquía de Hernán),
            # delegamos. Si no (stubs intermedios), seguimos sin error.
            if hasattr(servicio, "validar_parametros"):
                try:
                    servicio.validar_parametros(horas, personas=personas)
                except TypeError:
                    servicio.validar_parametros(horas)

            self._cliente = cliente
            self._servicio = servicio
            self._horas = float(horas)
            self._personas = personas
            self._estado = EstadoReserva.PENDIENTE
            self._fecha_creacion = datetime.now()
            self._fecha_confirmacion: datetime | None = None
            self._fecha_cancelacion: datetime | None = None
            self._costo_total: float = 0.0
            self._monto_pagado: float = 0.0
            self._historial_estados: list[tuple[EstadoReserva, datetime, str]] = [
                (EstadoReserva.PENDIENTE, self._fecha_creacion, "Reserva creada")
            ]
            self._notas: list[dict] = []

            _log.info(f"Reserva creada: [{self.identificador[:8]}] | "
                      f"Cliente: {cliente.nombre} | "
                      f"Servicio: {servicio.nombre} | Duración: {horas}h")
        except SoftwareFJError:
            raise
        except Exception as e:
            raise ReservaInvalidaError(
                f"Error inesperado al crear Reserva: {e}"
            ) from e

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def duracion_horas(self) -> float:
        """Alias de `horas` (nombre largo usado en la implementación original)."""
        return self._horas

    @property
    def personas(self) -> int:
        return self._personas

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def costo_final(self) -> float | None:
        """Costo final de la reserva (None si aún no se ha calculado)."""
        return self._costo_total if self._costo_total > 0 else None

    @property
    def monto_pagado(self) -> float:
        return self._monto_pagado

    @property
    def saldo_pendiente(self) -> float:
        return max(0.0, round(self._costo_total - self._monto_pagado, 2))

    # ── Transiciones de estado ──────────────────────────────────────────

    def _cambiar_estado(self, nuevo: EstadoReserva, motivo: str = "") -> None:
        permitidas = self.TRANSICIONES_VALIDAS.get(self._estado, set())
        if nuevo not in permitidas:
            raise OperacionNoPermitidaError(
                f"No se puede pasar de '{self._estado.value}' a '{nuevo.value}'."
            )
        self._estado = nuevo
        self._historial_estados.append((nuevo, datetime.now(), motivo))
        _log.info(f"[{self.identificador[:8]}] Estado -> {nuevo.value} | {motivo}")

    # ── Operaciones de ciclo de vida ────────────────────────────────────

    def confirmar(self, descuento: float = 0.0) -> float:
        """Confirma la reserva y calcula el costo total. PENDIENTE -> CONFIRMADA."""
        try:
            self._servicio.verificar_disponibilidad()
            es_premium = bool(getattr(self._cliente, "es_premium", False))
            try:
                # Servicio enriquecido (Hernán): acepta cliente_premium
                self._costo_total = self._servicio.calcular_costo(
                    self._horas,
                    descuento=descuento,
                    cliente_premium=es_premium,
                )
            except TypeError:
                # Servicio simple (stub): sin parámetro cliente_premium
                self._costo_total = self._servicio.calcular_costo(
                    self._horas, descuento=descuento
                )
        except SoftwareFJError as e:
            raise ReservaInvalidaError(
                f"No se pudo confirmar [{self.identificador[:8]}]: {e}"
            ) from e
        else:
            self._cambiar_estado(
                EstadoReserva.CONFIRMADA,
                f"Costo calculado: ${self._costo_total:.2f}",
            )
            self._fecha_confirmacion = datetime.now()
            return self._costo_total
        finally:
            _log.debug(
                f"[{self.identificador[:8]}] Intento de confirmación procesado."
            )

    def cancelar(self, motivo: str = "Cancelado por el cliente") -> dict:
        """
        Cancela la reserva. Aplica cargo del 10% si estaba CONFIRMADA.

        Compatible con la firma simple `cancelar()` del gestor (devuelve el
        dict, pero el gestor solo verifica que no se levante excepción).
        """
        try:
            if self._estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
                raise OperacionNoPermitidaError(
                    f"La reserva [{self.identificador[:8]}] en estado "
                    f"'{self._estado.value}' no puede cancelarse."
                )
            cargo = 0.0
            if self._estado is EstadoReserva.CONFIRMADA:
                cargo = round(self._costo_total * self.CARGO_CANCELACION, 2)
                _log.warning(
                    f"[{self.identificador[:8]}] Cancelación tardía: "
                    f"cargo {self.CARGO_CANCELACION*100:.0f}% = ${cargo:.2f}"
                )
            self._cambiar_estado(
                EstadoReserva.CANCELADA,
                f"{motivo} | Cargo cancelación: ${cargo:.2f}",
            )
            self._fecha_cancelacion = datetime.now()
            return {
                "reserva_id": self.identificador,
                "motivo": motivo,
                "cargo_cancelacion": cargo,
                "fecha": self._fecha_cancelacion.isoformat(),
            }
        except SoftwareFJError:
            raise
        except Exception as e:
            raise ReservaInvalidaError(
                f"Error al cancelar [{self.identificador[:8]}]: {e}"
            ) from e

    def procesar_pago(self, monto: float,
                      descuento_extra: float = 0.0,
                      metodo_pago: str = "efectivo",
                      cuotas: int = 1) -> dict:
        """
        SOBRECARGA: procesa el pago con distintas combinaciones de parámetros.

        Variantes:
            procesar_pago(monto)
            procesar_pago(monto, descuento_extra)
            procesar_pago(monto, descuento_extra, metodo_pago)
            procesar_pago(monto, descuento_extra, metodo_pago, cuotas)
        """
        metodos_validos = {"efectivo", "tarjeta", "transferencia"}
        try:
            if self._estado is not EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas confirmadas "
                    f"(estado actual: {self._estado.value})."
                )
            if not isinstance(monto, (int, float)) or monto <= 0:
                raise CalculoInconsistenteError(
                    "El monto debe ser un número positivo."
                )
            metodo = metodo_pago.lower().strip()
            if metodo not in metodos_validos:
                raise CalculoInconsistenteError(
                    f"Método de pago inválido '{metodo_pago}'. "
                    f"Válidos: {', '.join(sorted(metodos_validos))}."
                )
            if cuotas > 1 and metodo != "tarjeta":
                raise CalculoInconsistenteError(
                    "Las cuotas solo aplican para pagos con tarjeta."
                )
            if not isinstance(cuotas, int) or cuotas < 1:
                raise CalculoInconsistenteError(
                    "Cuotas debe ser un entero >= 1."
                )

            costo_efectivo = self._costo_total
            if descuento_extra > 0:
                if not (0 < descuento_extra <= 0.50):
                    raise CalculoInconsistenteError(
                        "descuento_extra debe estar entre 0 y 0.50."
                    )
                ajuste = round(costo_efectivo * descuento_extra, 2)
                costo_efectivo = round(costo_efectivo - ajuste, 2)
                _log.info(
                    f"[{self.identificador[:8]}] Descuento extra "
                    f"{descuento_extra*100:.0f}% aplicado: -${ajuste:.2f}"
                )

            saldo = round(costo_efectivo - self._monto_pagado, 2)
            if monto < saldo:
                raise CalculoInconsistenteError(
                    f"Monto ${monto:.2f} insuficiente. "
                    f"Saldo pendiente: ${self.saldo_pendiente:.2f}."
                )

            cargo_cuotas = 0.0
            if cuotas > 1:
                cargo_cuotas = round(monto * 0.015 * (cuotas - 1), 2)

            monto_final = round(monto + cargo_cuotas, 2)
            self._monto_pagado += monto_final

            self._cambiar_estado(
                EstadoReserva.PROCESADA,
                f"Pago de ${monto_final:.2f} vía {metodo} | {cuotas} cuota(s)",
            )

            comprobante = {
                "reserva_id": self.identificador,
                "cliente": self._cliente.nombre,
                "servicio": self._servicio.nombre,
                "duracion": f"{self._horas}h",
                "costo_total": self._costo_total,
                "descuento_extra": f"{descuento_extra*100:.0f}%",
                "cargo_cuotas": cargo_cuotas,
                "monto_pagado": self._monto_pagado,
                "metodo_pago": metodo,
                "cuotas": cuotas,
                "saldo": self.saldo_pendiente,
                "estado": self._estado.value,
                "timestamp": datetime.now().isoformat(),
            }
            _log.info(
                f"[{self.identificador[:8]}] Pago procesado: "
                f"${monto_final:.2f} | Método: {metodo}"
            )
            return comprobante
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoInconsistenteError(str(e)) from e
        finally:
            _log.debug(f"[{self.identificador[:8]}] Intento de pago procesado.")

    def completar(self) -> bool:
        """PROCESADA -> COMPLETADA."""
        self._cambiar_estado(EstadoReserva.COMPLETADA, "Servicio prestado exitosamente.")
        return True

    def procesar(self) -> float:
        """
        Atajo invocado por el GestorSistema:
            confirmar() + procesar_pago(costo_total)

        Devuelve el costo final, manteniendo retrocompatibilidad con el
        contrato original del stub (`reserva.procesar() -> float`).
        Deja la reserva en estado PROCESADA; `completar()` debe invocarse
        explícitamente cuando el servicio efectivamente se preste.
        """
        if self._estado is EstadoReserva.PENDIENTE:
            self.confirmar()
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas "
                f"(estado actual: {self._estado.value})."
            )
        self.procesar_pago(self._costo_total)
        return self._costo_total

    # ── Métodos accesorios ──────────────────────────────────────────────

    def agregar_nota(self, nota: str) -> None:
        if nota and isinstance(nota, str):
            self._notas.append({
                "nota": nota.strip(),
                "timestamp": datetime.now().isoformat(),
            })
            _log.debug(f"[{self.identificador[:8]}] Nota: {nota}")

    def obtener_resumen(self) -> str:
        historial = "\n".join(
            f"    [{ts.strftime('%H:%M:%S')}] {est.value.upper()} - {mot}"
            for est, ts, mot in self._historial_estados
        )
        return (
            f"\n+-- RESERVA {self.identificador[:8]} --------------+\n"
            f"  Cliente    : {self._cliente.nombre}\n"
            f"  Servicio   : {self._servicio.nombre}\n"
            f"  Duración   : {self._horas}h\n"
            f"  Estado     : {self._estado.value.upper()}\n"
            f"  Costo total: ${self._costo_total:.2f}\n"
            f"  Pagado     : ${self._monto_pagado:.2f}\n"
            f"  Saldo      : ${self.saldo_pendiente:.2f}\n"
            f"  Creada     : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
            f"  Historial:\n{historial}\n"
            f"+----------------------------------------------+"
        )

    def describir(self) -> str:
        return (f"Reserva #{self.identificador[:6]} - {self._cliente.nombre} "
                f"-> {self._servicio.nombre} ({self._horas}h) "
                f"- {self._estado.value}")

    def validar(self) -> None:
        if self._horas <= 0:
            raise ReservaInvalidaError("Duración debe ser > 0.")

    def __str__(self) -> str:
        return (f"Reserva [{self.identificador[:8]}] | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._horas}h | "
                f"{self._estado.value.upper()}")

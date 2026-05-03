"""
=============================================================
Universidad Nacional Abierta y a Distancia - UNAD
Curso: Programación - Código: 213023
Fase 4 - Prácticas Simuladas

Módulo 4: Clase Reserva — Estados, Sobrecarga y Excepciones
Empresa: Software FJ

Integrante: Hernán David Olaya Martínez
Rama GitHub: feat/reservas  (colaborando por ausencia del titular)
Issue: #4
=============================================================

CONCEPTOS APLICADOS:
    - Encapsulación: atributos privados con properties
    - Sobrecarga: procesar_pago() con variantes de parámetros
    - Manejo avanzado de excepciones:
        * try / except
        * try / except / else
        * try / except / finally
        * Encadenamiento de excepciones (raise ... from ...)
        * Excepciones personalizadas con códigos SFJ-4XX
    - Logging: registro de todos los eventos y errores en archivo
    - Integración: usa las clases de servicios.py (módulo 3)

IMPORTACIÓN:
    from servicios import ReservaSala, AlquilerEquipo,
                         AsesoriaEspecializada, ServicioError
    from reservas import Reserva, GestorReservas
"""

import logging
import os
from datetime import datetime
from enum import Enum

# Importa clases del Módulo 3 (feat/servicios)
from servicios import (
    Servicio, ServicioError, ServicioNoDisponibleError,
    ParametroInvalidoError, CostoInvalidoError,
    ReservaSala, AlquilerEquipo, AsesoriaEspecializada,
    configurar_logger
)


# =============================================================
# LOGGER DEL MÓDULO
# =============================================================
logger = configurar_logger("SFJ.reservas")


# =============================================================
# ENUMERACIÓN: EstadoReserva
# Define los posibles estados del ciclo de vida de una reserva
# =============================================================
class EstadoReserva(Enum):
    """
    Enumeración de estados válidos para una Reserva.

    Ciclo de vida:
        PENDIENTE → CONFIRMADA → PROCESADA → COMPLETADA
                 ↘ CANCELADA (desde PENDIENTE o CONFIRMADA)
    """
    PENDIENTE   = "pendiente"
    CONFIRMADA  = "confirmada"
    PROCESADA   = "procesada"
    COMPLETADA  = "completada"
    CANCELADA   = "cancelada"


# =============================================================
# EXCEPCIONES PERSONALIZADAS DEL MÓDULO DE RESERVAS
# Códigos SFJ-4XX para trazabilidad
# =============================================================

class ReservaError(Exception):
    """Excepción base de errores del módulo de Reservas."""
    def __init__(self, mensaje: str, codigo: str = "SFJ-400"):
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(f"[{codigo}] {mensaje}")
        logger.error(f"[{codigo}] {mensaje}")


class ReservaDuplicadaError(ReservaError):
    """Error al intentar crear una reserva con ID ya existente."""
    def __init__(self, reserva_id: str):
        super().__init__(
            f"Ya existe una reserva con ID '{reserva_id}'.",
            codigo="SFJ-401"
        )


class TransicionEstadoInvalidaError(ReservaError):
    """Error al intentar cambiar a un estado no permitido."""
    def __init__(self, estado_actual: str, estado_destino: str):
        super().__init__(
            f"No se puede pasar de '{estado_actual}' a '{estado_destino}'.",
            codigo="SFJ-402"
        )


class PagoInvalidoError(ReservaError):
    """Error cuando el monto de pago es inválido o insuficiente."""
    def __init__(self, detalle: str):
        super().__init__(
            f"Pago inválido: {detalle}",
            codigo="SFJ-403"
        )


class ReservaNoEncontradaError(ReservaError):
    """Error cuando no se encuentra una reserva solicitada."""
    def __init__(self, reserva_id: str):
        super().__init__(
            f"No existe ninguna reserva con ID '{reserva_id}'.",
            codigo="SFJ-404"
        )


class CancelacionNoPermitidaError(ReservaError):
    """Error al intentar cancelar una reserva que no puede cancelarse."""
    def __init__(self, reserva_id: str, estado_actual: str):
        super().__init__(
            f"La reserva '{reserva_id}' en estado '{estado_actual}' "
            f"no puede cancelarse.",
            codigo="SFJ-405"
        )


class ClienteInvalidoError(ReservaError):
    """Error cuando los datos del cliente son inválidos."""
    def __init__(self, campo: str, razon: str):
        super().__init__(
            f"Cliente inválido — campo '{campo}': {razon}",
            codigo="SFJ-406"
        )


# =============================================================
# CLASE: Cliente
# Representa al cliente que realiza la reserva
# =============================================================

class Cliente:
    """
    Representa un cliente de Software FJ con validaciones robustas
    y encapsulación de datos personales.

    Atributos privados:
        __nombre, __email, __telefono, __cliente_id, __es_premium
    """

    def __init__(self, cliente_id: str, nombre: str,
                 email: str, telefono: str = "",
                 es_premium: bool = False):
        """
        Constructor de Cliente con validaciones estrictas.

        Args:
            cliente_id (str): Identificador único del cliente
            nombre (str): Nombre completo
            email (str): Correo electrónico válido
            telefono (str): Teléfono de contacto (opcional)
            es_premium (bool): True si es cliente con beneficios premium
        """
        try:
            # Valida cliente_id
            if not cliente_id or not isinstance(cliente_id, str):
                raise ClienteInvalidoError("cliente_id",
                                           "no puede estar vacío")

            # Valida nombre
            nombre_limpio = nombre.strip() if isinstance(nombre, str) else ""
            if len(nombre_limpio) < 2:
                raise ClienteInvalidoError("nombre",
                                           "debe tener al menos 2 caracteres")

            # Valida email básico
            email_limpio = email.strip() if isinstance(email, str) else ""
            if "@" not in email_limpio or "." not in email_limpio:
                raise ClienteInvalidoError("email",
                                           "formato inválido (debe contener @ y .)")

            # Asigna atributos privados
            self.__cliente_id  = cliente_id.upper().strip()
            self.__nombre      = nombre_limpio
            self.__email       = email_limpio.lower()
            self.__telefono    = telefono.strip() if isinstance(telefono, str) else ""
            self.__es_premium  = bool(es_premium)
            self.__fecha_registro = datetime.now()

            logger.info(f"Cliente registrado: '{self.__nombre}' "
                        f"[{self.__cliente_id}] | Premium: {self.__es_premium}")

        except ReservaError:
            raise
        except Exception as e:
            raise ClienteInvalidoError("general",
                                       f"error inesperado: {e}") from e

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def cliente_id(self) -> str:
        return self.__cliente_id

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def email(self) -> str:
        return self.__email

    @property
    def telefono(self) -> str:
        return self.__telefono

    @property
    def es_premium(self) -> bool:
        return self.__es_premium

    @property
    def fecha_registro(self) -> datetime:
        return self.__fecha_registro

    def __str__(self) -> str:
        premium = "⭐ Premium" if self.__es_premium else "Estándar"
        return (f"Cliente [{self.__cliente_id}] {self.__nombre} "
                f"| {self.__email} | {premium}")


# =============================================================
# CLASE: Reserva
# Integra Cliente + Servicio + duración + estado + pagos
# =============================================================

class Reserva:
    """
    Clase central del módulo 4.
    Integra un Cliente, un Servicio, una duración y un estado,
    e implementa confirmación, cancelación y procesamiento con
    manejo avanzado de excepciones.

    SOBRECARGA: procesar_pago() acepta distintas combinaciones
    de parámetros (monto, descuento_extra, metodo_pago, cuotas).

    Estados válidos y transiciones:
        PENDIENTE  → CONFIRMADA, CANCELADA
        CONFIRMADA → PROCESADA,  CANCELADA
        PROCESADA  → COMPLETADA
        COMPLETADA → (estado final, no transita)
        CANCELADA  → (estado final, no transita)
    """

    # Transiciones permitidas entre estados
    TRANSICIONES_VALIDAS = {
        EstadoReserva.PENDIENTE:   {EstadoReserva.CONFIRMADA,
                                    EstadoReserva.CANCELADA},
        EstadoReserva.CONFIRMADA:  {EstadoReserva.PROCESADA,
                                    EstadoReserva.CANCELADA},
        EstadoReserva.PROCESADA:   {EstadoReserva.COMPLETADA},
        EstadoReserva.COMPLETADA:  set(),   # Estado final
        EstadoReserva.CANCELADA:   set(),   # Estado final
    }

    # Cargo por cancelación tardía (10% del total)
    CARGO_CANCELACION = 0.10

    def __init__(self, reserva_id: str, cliente: Cliente,
                 servicio: Servicio, duracion_horas: float,
                 personas: int = 1):
        """
        Constructor de Reserva.

        Args:
            reserva_id (str): Identificador único de la reserva
            cliente (Cliente): Objeto Cliente validado
            servicio (Servicio): Objeto de servicio especializado
            duracion_horas (float): Duración solicitada en horas
            personas (int): Número de personas (para salas)
        """
        try:
            # Valida reserva_id
            if not reserva_id or not isinstance(reserva_id, str):
                raise ReservaError("reserva_id inválido", "SFJ-400")

            # Valida que cliente sea instancia de Cliente
            if not isinstance(cliente, Cliente):
                raise ReservaError(
                    "Se esperaba un objeto Cliente válido.", "SFJ-400"
                )

            # Valida que servicio sea instancia de Servicio
            if not isinstance(servicio, Servicio):
                raise ReservaError(
                    "Se esperaba un objeto Servicio válido.", "SFJ-400"
                )

            # Valida duración
            if not isinstance(duracion_horas, (int, float)) \
                    or duracion_horas <= 0:
                raise ParametroInvalidoError("duracion_horas",
                                             "debe ser un número positivo")

            # Valida disponibilidad del servicio (puede lanzar excepción)
            servicio.verificar_disponibilidad()

            # Valida parámetros específicos del servicio
            if isinstance(servicio, ReservaSala):
                servicio.validar_parametros(duracion_horas, personas=personas)
            else:
                servicio.validar_parametros(duracion_horas)

            # Asigna atributos privados
            self.__reserva_id     = reserva_id.upper().strip()
            self.__cliente        = cliente
            self.__servicio       = servicio
            self.__duracion_horas = float(duracion_horas)
            self.__personas       = personas
            self.__estado         = EstadoReserva.PENDIENTE
            self.__fecha_creacion = datetime.now()
            self.__fecha_confirmacion = None
            self.__fecha_cancelacion  = None
            self.__costo_total    = 0.0
            self.__monto_pagado   = 0.0
            self.__historial_estados = [
                (EstadoReserva.PENDIENTE, datetime.now(), "Reserva creada")
            ]
            self.__notas          = []

            logger.info(
                f"Reserva creada: [{self.__reserva_id}] | "
                f"Cliente: {cliente.nombre} | "
                f"Servicio: {servicio.nombre} | "
                f"Duración: {duracion_horas}h"
            )

        except (ReservaError, ServicioError):
            raise
        except Exception as e:
            raise ReservaError(
                f"Error inesperado al crear Reserva: {e}", "SFJ-400"
            ) from e

    # ── Properties ─────────────────────────────────────────────────────

    @property
    def reserva_id(self) -> str:
        return self.__reserva_id

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion_horas(self) -> float:
        return self.__duracion_horas

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    @property
    def monto_pagado(self) -> float:
        return self.__monto_pagado

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @property
    def saldo_pendiente(self) -> float:
        """Retorna cuánto falta por pagar."""
        return max(0.0, round(self.__costo_total - self.__monto_pagado, 2))

    # ── Métodos de ciclo de vida ────────────────────────────────────────

    def __cambiar_estado(self, nuevo_estado: EstadoReserva, motivo: str = ""):
        """
        Método privado que gestiona transiciones de estado validadas.

        Args:
            nuevo_estado: Estado al que se desea transitar
            motivo: Razón del cambio de estado

        Raises:
            TransicionEstadoInvalidaError
        """
        transiciones = self.TRANSICIONES_VALIDAS.get(self.__estado, set())
        if nuevo_estado not in transiciones:
            raise TransicionEstadoInvalidaError(
                self.__estado.value,
                nuevo_estado.value
            )
        self.__estado = nuevo_estado
        self.__historial_estados.append((nuevo_estado, datetime.now(), motivo))
        logger.info(
            f"[{self.__reserva_id}] Estado → {nuevo_estado.value} | {motivo}"
        )

    def confirmar(self, descuento: float = 0.0) -> float:
        """
        Confirma la reserva y calcula el costo total.
        Transición: PENDIENTE → CONFIRMADA

        Args:
            descuento (float): Descuento porcentual adicional (0.0–1.0)

        Returns:
            float: Costo total calculado

        Raises:
            TransicionEstadoInvalidaError, CostoInvalidoError
        """
        try:
            # try/except/else para diferenciar error de éxito
            self.__costo_total = self.__servicio.calcular_costo(
                self.__duracion_horas,
                descuento=descuento,
                cliente_premium=self.__cliente.es_premium
            )
        except ServicioError as e:
            # Encadenamiento: error de servicio encadenado a error de reserva
            raise ReservaError(
                f"No se pudo confirmar [{self.__reserva_id}]: {e.mensaje}",
                "SFJ-400"
            ) from e
        else:
            # Solo cambia estado si el cálculo fue exitoso
            self.__cambiar_estado(
                EstadoReserva.CONFIRMADA,
                f"Costo calculado: ${self.__costo_total:.2f}"
            )
            self.__fecha_confirmacion = datetime.now()
            logger.info(
                f"[{self.__reserva_id}] Confirmada | "
                f"Costo total: ${self.__costo_total:.2f}"
            )
            return self.__costo_total
        finally:
            # Siempre registra el intento de confirmación
            logger.debug(
                f"[{self.__reserva_id}] Intento de confirmación procesado."
            )

    def cancelar(self, motivo: str = "Cancelado por el cliente") -> dict:
        """
        Cancela la reserva.
        Aplica cargo de cancelación si ya estaba confirmada.
        Transición: PENDIENTE/CONFIRMADA → CANCELADA

        Args:
            motivo (str): Razón de la cancelación

        Returns:
            dict: Resumen con cargo de cancelación si aplica

        Raises:
            CancelacionNoPermitidaError
        """
        try:
            if self.__estado not in (EstadoReserva.PENDIENTE,
                                     EstadoReserva.CONFIRMADA):
                raise CancelacionNoPermitidaError(
                    self.__reserva_id,
                    self.__estado.value
                )

            cargo = 0.0
            # Si ya fue confirmada, se aplica cargo por cancelación tardía
            if self.__estado == EstadoReserva.CONFIRMADA:
                cargo = round(self.__costo_total * self.CARGO_CANCELACION, 2)
                logger.warning(
                    f"[{self.__reserva_id}] Cancelación tardía: "
                    f"cargo del {self.CARGO_CANCELACION*100:.0f}% "
                    f"= ${cargo:.2f}"
                )

            self.__cambiar_estado(
                EstadoReserva.CANCELADA,
                f"{motivo} | Cargo cancelación: ${cargo:.2f}"
            )
            self.__fecha_cancelacion = datetime.now()

            return {
                "reserva_id":   self.__reserva_id,
                "motivo":        motivo,
                "cargo_cancelacion": cargo,
                "fecha":         self.__fecha_cancelacion.isoformat()
            }

        except ReservaError:
            raise
        except Exception as e:
            raise ReservaError(
                f"Error al cancelar [{self.__reserva_id}]: {e}",
                "SFJ-400"
            ) from e

    def procesar_pago(self, monto: float,
                      descuento_extra: float = 0.0,
                      metodo_pago: str = "efectivo",
                      cuotas: int = 1) -> dict:
        """
        SOBRECARGA: procesa el pago de la reserva con distintas variantes.

        Variantes de llamada (simulando sobrecarga):
            procesar_pago(monto)
            procesar_pago(monto, descuento_extra)
            procesar_pago(monto, descuento_extra, metodo_pago)
            procesar_pago(monto, descuento_extra, metodo_pago, cuotas)

        Args:
            monto (float): Monto a pagar en esta transacción
            descuento_extra (float): Descuento adicional por promoción
            metodo_pago (str): efectivo, tarjeta, transferencia
            cuotas (int): Número de cuotas (solo para tarjeta)

        Returns:
            dict: Comprobante del pago con detalles

        Raises:
            TransicionEstadoInvalidaError, PagoInvalidoError
        """
        metodos_validos = {"efectivo", "tarjeta", "transferencia"}

        try:
            # Solo se puede pagar en estado CONFIRMADA
            if self.__estado != EstadoReserva.CONFIRMADA:
                raise TransicionEstadoInvalidaError(
                    self.__estado.value,
                    "PROCESADA (requiere estado CONFIRMADA)"
                )

            # Valida monto
            if not isinstance(monto, (int, float)) or monto <= 0:
                raise PagoInvalidoError(
                    "el monto debe ser un número positivo"
                )

            # Valida método de pago
            metodo = metodo_pago.lower().strip()
            if metodo not in metodos_validos:
                raise PagoInvalidoError(
                    f"método inválido '{metodo_pago}'. "
                    f"Use: {', '.join(metodos_validos)}"
                )

            # Cuotas solo aplica para tarjeta
            if cuotas > 1 and metodo != "tarjeta":
                raise PagoInvalidoError(
                    "las cuotas solo aplican para pagos con tarjeta"
                )
            if not isinstance(cuotas, int) or cuotas < 1:
                raise PagoInvalidoError("cuotas debe ser un entero ≥ 1")

            # Aplica descuento extra si hay
            costo_efectivo = self.__costo_total
            if descuento_extra > 0:
                if not isinstance(descuento_extra, (int, float)) \
                        or not (0 < descuento_extra <= 0.50):
                    raise PagoInvalidoError(
                        "descuento_extra debe estar entre 0 y 0.50"
                    )
                ajuste = round(costo_efectivo * descuento_extra, 2)
                costo_efectivo = round(costo_efectivo - ajuste, 2)
                logger.info(
                    f"[{self.__reserva_id}] Descuento extra "
                    f"{descuento_extra*100:.0f}% aplicado: -${ajuste:.2f}"
                )

            # Verifica que el monto cubra el saldo pendiente
            if monto < round(costo_efectivo - self.__monto_pagado, 2):
                raise PagoInvalidoError(
                    f"monto ${monto:.2f} insuficiente. "
                    f"Saldo pendiente: ${self.saldo_pendiente:.2f}"
                )

            # Calcula cargo por cuotas (1.5% por cuota adicional)
            cargo_cuotas = 0.0
            if cuotas > 1:
                cargo_cuotas = round(monto * 0.015 * (cuotas - 1), 2)
                logger.info(
                    f"[{self.__reserva_id}] Cargo por {cuotas} cuotas: "
                    f"+${cargo_cuotas:.2f}"
                )

            monto_final = round(monto + cargo_cuotas, 2)
            self.__monto_pagado += monto_final

            # Cambia estado a PROCESADA si el pago cubre el total
            self.__cambiar_estado(
                EstadoReserva.PROCESADA,
                f"Pago de ${monto_final:.2f} vía {metodo} | "
                f"{cuotas} cuota(s)"
            )

            comprobante = {
                "reserva_id":    self.__reserva_id,
                "cliente":       self.__cliente.nombre,
                "servicio":      self.__servicio.nombre,
                "duracion":      f"{self.__duracion_horas}h",
                "costo_total":   self.__costo_total,
                "descuento_extra": f"{descuento_extra*100:.0f}%",
                "cargo_cuotas":  cargo_cuotas,
                "monto_pagado":  self.__monto_pagado,
                "metodo_pago":   metodo,
                "cuotas":        cuotas,
                "saldo":         self.saldo_pendiente,
                "estado":        self.__estado.value,
                "timestamp":     datetime.now().isoformat()
            }

            logger.info(
                f"[{self.__reserva_id}] Pago procesado: "
                f"${monto_final:.2f} | Método: {metodo}"
            )
            return comprobante

        except (ReservaError, ServicioError):
            raise
        except Exception as e:
            raise PagoInvalidoError(str(e)) from e

        finally:
            logger.debug(
                f"[{self.__reserva_id}] Intento de pago procesado."
            )

    def completar(self) -> bool:
        """
        Marca la reserva como completada.
        Transición: PROCESADA → COMPLETADA

        Returns:
            bool: True si se completó exitosamente
        """
        try:
            self.__cambiar_estado(
                EstadoReserva.COMPLETADA,
                "Servicio prestado exitosamente."
            )
            logger.info(f"[{self.__reserva_id}] ✅ Reserva COMPLETADA.")
            return True
        except TransicionEstadoInvalidaError:
            raise

    def agregar_nota(self, nota: str):
        """Agrega una nota informativa a la reserva."""
        if nota and isinstance(nota, str):
            self.__notas.append({
                "nota": nota.strip(),
                "timestamp": datetime.now().isoformat()
            })
            logger.debug(f"[{self.__reserva_id}] Nota: {nota}")

    def obtener_resumen(self) -> str:
        """Retorna un resumen completo del estado de la reserva."""
        historial_str = "\n".join(
            f"    [{ts.strftime('%H:%M:%S')}] {est.value.upper()} — {mot}"
            for est, ts, mot in self.__historial_estados
        )
        return (
            f"\n╔══ RESERVA {self.__reserva_id} ═══════════════════════╗\n"
            f"  Cliente    : {self.__cliente.nombre} "
            f"[{self.__cliente.cliente_id}]\n"
            f"  Servicio   : {self.__servicio.nombre}\n"
            f"  Duración   : {self.__duracion_horas}h\n"
            f"  Estado     : {self.__estado.value.upper()}\n"
            f"  Costo total: ${self.__costo_total:.2f}\n"
            f"  Pagado     : ${self.__monto_pagado:.2f}\n"
            f"  Saldo      : ${self.saldo_pendiente:.2f}\n"
            f"  Creada     : {self.__fecha_creacion.strftime('%Y-%m-%d %H:%M')}\n"
            f"  Historial de estados:\n{historial_str}\n"
            f"╚═══════════════════════════════════════════════╝"
        )

    def __str__(self) -> str:
        return (f"Reserva [{self.__reserva_id}] | "
                f"{self.__cliente.nombre} | {self.__servicio.nombre} | "
                f"{self.__duracion_horas}h | {self.__estado.value.upper()}")


# =============================================================
# CLASE: GestorReservas
# Administra la lista interna de reservas con validaciones
# =============================================================

class GestorReservas:
    """
    Gestiona la lista interna de reservas de Software FJ.
    No usa base de datos; todo se gestiona en memoria con listas.

    Métodos principales:
        - agregar_reserva()
        - buscar_reserva()
        - confirmar_reserva()
        - cancelar_reserva()
        - pagar_reserva()
        - completar_reserva()
        - listar_reservas()
    """

    def __init__(self):
        """Inicializa el gestor con lista vacía de reservas."""
        self.__reservas: dict[str, Reserva] = {}
        logger.info("GestorReservas inicializado.")

    def agregar_reserva(self, reserva: Reserva) -> bool:
        """
        Agrega una nueva reserva al sistema.

        Args:
            reserva (Reserva): Objeto Reserva ya construido

        Returns:
            bool: True si se agregó correctamente

        Raises:
            ReservaDuplicadaError, ReservaError
        """
        try:
            if not isinstance(reserva, Reserva):
                raise ReservaError(
                    "Se esperaba un objeto Reserva válido.", "SFJ-400"
                )
            rid = reserva.reserva_id
            if rid in self.__reservas:
                raise ReservaDuplicadaError(rid)

            self.__reservas[rid] = reserva
            logger.info(f"GestorReservas: reserva '{rid}' agregada. "
                        f"Total: {len(self.__reservas)}")
            return True

        except ReservaError:
            raise
        except Exception as e:
            raise ReservaError(
                f"Error al agregar reserva: {e}", "SFJ-400"
            ) from e

    def buscar_reserva(self, reserva_id: str) -> Reserva:
        """
        Busca y retorna una reserva por su ID.

        Raises:
            ReservaNoEncontradaError
        """
        rid = reserva_id.upper().strip() \
            if isinstance(reserva_id, str) else ""
        if rid not in self.__reservas:
            raise ReservaNoEncontradaError(rid)
        return self.__reservas[rid]

    def confirmar_reserva(self, reserva_id: str,
                          descuento: float = 0.0) -> float:
        """Confirma una reserva y retorna su costo total."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            costo = reserva.confirmar(descuento=descuento)
            return costo
        except ReservaError:
            raise

    def cancelar_reserva(self, reserva_id: str,
                         motivo: str = "Cancelado") -> dict:
        """Cancela una reserva existente."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            return reserva.cancelar(motivo)
        except ReservaError:
            raise

    def pagar_reserva(self, reserva_id: str, monto: float,
                      descuento_extra: float = 0.0,
                      metodo_pago: str = "efectivo",
                      cuotas: int = 1) -> dict:
        """Procesa el pago de una reserva (sobrecarga)."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            return reserva.procesar_pago(
                monto,
                descuento_extra=descuento_extra,
                metodo_pago=metodo_pago,
                cuotas=cuotas
            )
        except ReservaError:
            raise

    def completar_reserva(self, reserva_id: str) -> bool:
        """Marca la reserva como completada."""
        try:
            reserva = self.buscar_reserva(reserva_id)
            return reserva.completar()
        except ReservaError:
            raise

    def listar_reservas(self, filtro_estado: EstadoReserva = None) -> list:
        """
        Lista todas las reservas, opcionalmente filtradas por estado.

        Args:
            filtro_estado: Si se especifica, filtra por ese estado

        Returns:
            list: Lista de objetos Reserva
        """
        if filtro_estado:
            return [r for r in self.__reservas.values()
                    if r.estado == filtro_estado]
        return list(self.__reservas.values())

    def resumen_general(self) -> str:
        """Genera un resumen estadístico de todas las reservas."""
        total = len(self.__reservas)
        por_estado = {}
        ingresos = 0.0
        for r in self.__reservas.values():
            est = r.estado.value
            por_estado[est] = por_estado.get(est, 0) + 1
            if r.estado in (EstadoReserva.PROCESADA,
                            EstadoReserva.COMPLETADA):
                ingresos += r.monto_pagado

        detalle = " | ".join(
            f"{k}: {v}" for k, v in por_estado.items()
        )
        return (
            f"\n══ RESUMEN GESTOR DE RESERVAS ══════════════\n"
            f"  Total reservas : {total}\n"
            f"  Por estado     : {detalle}\n"
            f"  Ingresos pag.  : ${ingresos:.2f}\n"
            f"════════════════════════════════════════════"
        )


# =============================================================
# DEMOSTRACIÓN DEL MÓDULO 4
# 10+ operaciones válidas e inválidas
# =============================================================

def demostrar_modulo_reservas():
    """
    Simula más de 10 operaciones completas del módulo de reservas,
    incluyendo casos válidos e inválidos, demostrando:
        - Ciclo completo de una reserva
        - Sobrecarga de procesar_pago()
        - try/except, try/except/else, try/except/finally
        - Encadenamiento de excepciones
        - Logging automático en archivo
    """
    print("\n" + "="*58)
    print("  SOFTWARE FJ — MÓDULO 4: RESERVAS")
    print("  Integrante: Hernán David Olaya Martínez")
    print("="*58)

    gestor = GestorReservas()

    # ── Servicios del Módulo 3 ──────────────────────────────────────
    sala_a1   = ReservaSala("SALA-A1", 10, 50.0, equipada=True)
    equipo_01 = AlquilerEquipo("EQ-001", "laptop", 20.0)
    asesoria  = AsesoriaEspecializada("ASE-001", "seguridad",
                                      80.0, "experto", "virtual")

    # ── Clientes ────────────────────────────────────────────────────
    print("\n▶ OP-1 y OP-2: Registro de clientes válidos e inválidos")
    try:
        c1 = Cliente("CLI-001", "Hernán Olaya",
                     "hernan@email.com", es_premium=True)
        c2 = Cliente("CLI-002", "Ana Gómez",
                     "ana.gomez@empresa.co", es_premium=False)
        print(f"  ✅ {c1}")
        print(f"  ✅ {c2}")
    except ReservaError as e:
        print(f"  ✗ {e}")

    # Cliente con email inválido
    print("\n▶ OP-3: Cliente con email inválido")
    try:
        c_malo = Cliente("CLI-BAD", "X", "email-sin-arroba")
    except ClienteInvalidoError as e:
        print(f"  Capturado → {e}")

    # ── Reservas válidas ────────────────────────────────────────────
    print("\n▶ OP-4: Crear reserva de sala (válida)")
    try:
        r1 = Reserva("RES-001", c1, sala_a1, duracion_horas=3, personas=6)
        gestor.agregar_reserva(r1)
        print(f"  ✅ {r1}")
    except (ReservaError, ServicioError) as e:
        print(f"  ✗ {e}")

    print("\n▶ OP-5: Crear reserva de equipo (válida)")
    try:
        r2 = Reserva("RES-002", c2, equipo_01, duracion_horas=8)
        gestor.agregar_reserva(r2)
        print(f"  ✅ {r2}")
    except (ReservaError, ServicioError) as e:
        print(f"  ✗ {e}")

    print("\n▶ OP-6: Crear reserva de asesoría (válida)")
    try:
        r3 = Reserva("RES-003", c1, asesoria, duracion_horas=2)
        gestor.agregar_reserva(r3)
        print(f"  ✅ {r3}")
    except (ReservaError, ServicioError) as e:
        print(f"  ✗ {e}")

    # ── Reserva duplicada ───────────────────────────────────────────
    print("\n▶ OP-7: Reserva con ID duplicado")
    try:
        r_dup = Reserva("RES-001", c2, equipo_01, duracion_horas=4)
        gestor.agregar_reserva(r_dup)
    except ReservaDuplicadaError as e:
        print(f"  Capturado → {e}")

    # ── Confirmar reservas ──────────────────────────────────────────
    print("\n▶ OP-8: Confirmar reservas (try/except/else/finally)")
    for rid in ["RES-001", "RES-002", "RES-003"]:
        try:
            costo = gestor.confirmar_reserva(rid, descuento=0.05)
        except (ReservaError, ServicioError) as e:
            print(f"  ✗ [{rid}] {e}")
        else:
            print(f"  ✅ [{rid}] Confirmada | Costo: ${costo:.2f}")
        finally:
            print(f"     (bloque finally ejecutado para {rid})")

    # ── Procesar pagos con sobrecarga ───────────────────────────────
    print("\n▶ OP-9: Procesar pagos (sobrecarga de procesar_pago)")

    # Modo 1: solo monto
    try:
        comp = gestor.pagar_reserva("RES-001",
                                    monto=gestor.buscar_reserva(
                                        "RES-001").costo_total)
        print(f"  ✅ [RES-001] Pago en efectivo: "
              f"${comp['monto_pagado']:.2f}")
    except ReservaError as e:
        print(f"  ✗ {e}")

    # Modo 2: monto + descuento extra + tarjeta en cuotas
    try:
        monto2 = gestor.buscar_reserva("RES-002").costo_total
        comp2 = gestor.pagar_reserva("RES-002", monto=monto2,
                                     descuento_extra=0.05,
                                     metodo_pago="tarjeta",
                                     cuotas=3)
        print(f"  ✅ [RES-002] Pago tarjeta 3 cuotas: "
              f"${comp2['monto_pagado']:.2f}")
    except ReservaError as e:
        print(f"  ✗ {e}")

    # Modo 3: transferencia sin cuotas
    try:
        monto3 = gestor.buscar_reserva("RES-003").costo_total
        comp3 = gestor.pagar_reserva("RES-003", monto=monto3,
                                     metodo_pago="transferencia")
        print(f"  ✅ [RES-003] Pago transferencia: "
              f"${comp3['monto_pagado']:.2f}")
    except ReservaError as e:
        print(f"  ✗ {e}")

    # ── Pago inválido ───────────────────────────────────────────────
    print("\n▶ OP-10: Pago con método inválido")
    try:
        # Necesita una reserva en estado CONFIRMADA
        r4 = Reserva("RES-004", c2, sala_a1, duracion_horas=2)
        gestor.agregar_reserva(r4)
        gestor.confirmar_reserva("RES-004")
        gestor.pagar_reserva("RES-004", monto=50.0,
                             metodo_pago="bitcoin")
    except PagoInvalidoError as e:
        print(f"  Capturado → {e}")

    # ── Cancelar una reserva ────────────────────────────────────────
    print("\n▶ OP-11: Cancelar reserva pendiente")
    try:
        r5 = Reserva("RES-005", c1, equipo_01, duracion_horas=5)
        gestor.agregar_reserva(r5)
        resultado = gestor.cancelar_reserva("RES-005",
                                            "Cliente no disponible")
        print(f"  ✅ Cancelada: cargo=${resultado['cargo_cancelacion']:.2f}")
    except ReservaError as e:
        print(f"  ✗ {e}")

    # ── Completar reservas pagadas ──────────────────────────────────
    print("\n▶ OP-12: Completar reservas procesadas")
    for rid in ["RES-001", "RES-002", "RES-003"]:
        try:
            gestor.completar_reserva(rid)
            print(f"  ✅ [{rid}] COMPLETADA")
        except ReservaError as e:
            print(f"  ✗ [{rid}] {e}")

    # ── Resumen general ─────────────────────────────────────────────
    print(gestor.resumen_general())

    # ── Detalle de una reserva ──────────────────────────────────────
    print("\n▶ Detalle completo de RES-001:")
    try:
        print(gestor.buscar_reserva("RES-001").obtener_resumen())
    except ReservaNoEncontradaError as e:
        print(f"  ✗ {e}")

    print("\n✅ Módulo 4 completado. Logs en logs/software_fj.log\n")
    print("="*58)


# =============================================================
# PUNTO DE ENTRADA — ejecuta ambos módulos juntos
# =============================================================
if __name__ == "__main__":
    # Primero demuestra los servicios (Módulo 3)
    from servicios import demostrar_modulo_servicios
    demostrar_modulo_servicios()

    # Luego demuestra las reservas (Módulo 4)
    demostrar_modulo_reservas()

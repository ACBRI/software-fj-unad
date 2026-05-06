"""
ReservaSala — servicio especializado para reserva de salas.

Implementación original: Hernán David Olaya Martínez (issue #3, rama feat/servicios)
Integración con el núcleo del sistema: Andrés Camilo Briñez Núñez

POLIMORFISMO: sobrescribe calcular_costo(), describir() y validar_parametros()
con lógica específica de salas (recargo por equipamiento, capacidad máxima).
"""

from __future__ import annotations

from src.core.excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    SoftwareFJError,
)
from src.core.logger import obtener_logger
from src.modelos.servicio import Servicio

_log = obtener_logger(__name__)


class ReservaSala(Servicio):
    """Reserva de salas de reuniones o trabajo en Software FJ."""

    DURACION_MINIMA = 1.0   # Mínimo 1 hora
    DURACION_MAXIMA = 8.0   # Máximo 8 horas por reserva
    TARIFA_EQUIPADA = 1.3   # +30% si la sala está equipada

    def __init__(self, sala_id: str, capacidad_maxima: int,
                 tarifa_base: float, equipada: bool = False):
        try:
            if not sala_id or not isinstance(sala_id, str):
                raise DatosInvalidosError(
                    "Parámetro inválido 'sala_id': debe ser un identificador válido."
                )
            if not isinstance(capacidad_maxima, int) or capacidad_maxima < 1:
                raise DatosInvalidosError(
                    "Parámetro inválido 'capacidad_maxima': debe ser un entero positivo."
                )

            nombre = f"Sala {sala_id}"
            super().__init__(nombre, tarifa_base,
                             "Reserva de sala de reuniones o trabajo")

            self.__sala_id = sala_id.upper().strip()
            self.__capacidad_maxima = capacidad_maxima
            self.__equipada = equipada
            self.__personas_reserva = 0

            _log.info(f"ReservaSala '{self.__sala_id}' creada | "
                      f"Cap: {capacidad_maxima} personas | Equipada: {equipada}")
        except SoftwareFJError:
            raise
        except Exception as e:
            raise SoftwareFJError(
                f"Error al crear ReservaSala: {e}"
            ) from e

    @property
    def sala_id(self) -> str:
        return self.__sala_id

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    @property
    def equipada(self) -> bool:
        return self.__equipada

    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        POLIMORFISMO + SOBRECARGA: calcula el costo de reservar la sala.

        Lógica específica:
            - Si la sala está equipada: +30% sobre tarifa base.
            - Cliente premium: -10% adicional de descuento.
            - Impuesto: usa IVA general si no se especifica.
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion_horas)

            tarifa = self.tarifa_base
            if self.__equipada:
                tarifa *= self.TARIFA_EQUIPADA

            costo_base = tarifa * duracion_horas

            descuento_total = descuento
            if cliente_premium:
                descuento_total += 0.10

            descuento_total = min(descuento_total, 0.50)
            costo_con_descuento = costo_base * (1 - descuento_total)

            tasa_impuesto = impuesto if impuesto is not None else self.IVA_GENERAL
            if not isinstance(tasa_impuesto, (int, float)) or tasa_impuesto < 0:
                raise DatosInvalidosError(
                    "Parámetro inválido 'impuesto': debe ser un número no negativo."
                )

            costo_final = costo_con_descuento * (1 + tasa_impuesto)

            if costo_final < 0:
                raise CalculoInconsistenteError(
                    f"Cálculo de costo con resultado negativo: ${costo_final:.2f}"
                )

            detalle = (f"Sala {self.__sala_id} | {duracion_horas}h | "
                       f"Equipada={self.__equipada} | "
                       f"Desc={descuento_total*100:.0f}% | "
                       f"IVA={tasa_impuesto*100:.0f}% | "
                       f"Premium={cliente_premium}")
            self._registrar_calculo(costo_final, detalle)

            return round(costo_final, 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoInconsistenteError(str(e)) from e
        finally:
            _log.debug(f"[ReservaSala-{self.__sala_id}] "
                       f"Intento de cálculo de costo completado.")

    def describir(self) -> str:
        equipamiento = ("Proyector, pantalla, sistema de audio"
                        if self.__equipada else "Sin equipamiento adicional")
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"+-- RESERVA DE SALA -------------------------+\n"
            f"  ID Sala       : {self.__sala_id}\n"
            f"  Capacidad     : {self.__capacidad_maxima} personas\n"
            f"  Tarifa base   : ${self.tarifa_base:.2f}/hora\n"
            f"  Equipamiento  : {equipamiento}\n"
            f"  Extra equipada: +{(self.TARIFA_EQUIPADA-1)*100:.0f}% sobre tarifa\n"
            f"  Duración      : {self.DURACION_MINIMA}h - {self.DURACION_MAXIMA}h\n"
            f"  Estado        : {estado}\n"
            f"+--------------------------------------------+"
        )

    def validar_parametros(self, duracion_horas: float,
                           personas: int = 0, **kwargs) -> bool:
        try:
            if not isinstance(duracion_horas, (int, float)):
                raise DatosInvalidosError(
                    "Parámetro inválido 'duracion_horas': debe ser un número."
                )
            if not (self.DURACION_MINIMA <= duracion_horas <= self.DURACION_MAXIMA):
                raise DatosInvalidosError(
                    f"Duración {duracion_horas}h fuera del rango permitido "
                    f"[{self.DURACION_MINIMA}h - {self.DURACION_MAXIMA}h]."
                )
            if personas > 0:
                if not isinstance(personas, int):
                    raise DatosInvalidosError(
                        "Parámetro inválido 'personas': debe ser un entero."
                    )
                if personas > self.__capacidad_maxima:
                    raise DatosInvalidosError(
                        f"Servicio '{self.nombre}': capacidad máxima "
                        f"{self.__capacidad_maxima}, solicitada {personas}."
                    )
                self.__personas_reserva = personas

            _log.debug(f"[ReservaSala-{self.__sala_id}] "
                       f"Parámetros válidos: {duracion_horas}h, {personas} personas")
            return True
        except SoftwareFJError:
            raise
        except Exception as e:
            raise DatosInvalidosError(f"Error de validación: {e}") from e

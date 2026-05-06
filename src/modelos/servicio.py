"""
Clase abstracta Servicio del sistema Software FJ.

Implementación original: Hernán David Olaya Martínez (issue #3, rama feat/servicios)
Integración con el núcleo del sistema: Andrés Camilo Briñez Núñez

CONCEPTOS APLICADOS:
    - Abstracción: clase abstracta Servicio con métodos abstractos
    - Herencia: Servicio hereda de EntidadBase (jerarquía POO del proyecto)
    - Encapsulación: atributos privados con properties
    - Manejo de excepciones: try/except/else/finally, encadenamiento,
      excepciones personalizadas del núcleo (SoftwareFJError)
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime

from src.core.entidad_base import EntidadBase
from src.core.excepciones import (
    DatosInvalidosError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from src.core.logger import obtener_logger

_log = obtener_logger(__name__)


class Servicio(EntidadBase):
    """
    Clase abstracta que representa un servicio genérico de Software FJ.

    Subclases concretas:
        - ReservaSala
        - AlquilerEquipo
        - AsesoriaEspecializada
    """

    IVA_GENERAL = 0.19  # Impuesto general de la empresa

    def __init__(self, nombre: str, tarifa_base: float,
                 descripcion_breve: str = ""):
        """Constructor de la clase abstracta."""
        try:
            super().__init__()  # genera identificador y timestamp en EntidadBase

            if not nombre or not isinstance(nombre, str):
                raise DatosInvalidosError(
                    "Parámetro inválido 'nombre': debe ser una cadena no vacía."
                )
            if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
                raise DatosInvalidosError(
                    "Parámetro inválido 'tarifa_base': debe ser un número positivo."
                )

            self.__nombre = nombre.strip()
            self.__tarifa_base = float(tarifa_base)
            self.__descripcion_breve = descripcion_breve
            self.__disponible = True
            self.__fecha_creacion = datetime.now()
            self._historial_costos = []

            _log.info(f"Servicio creado: '{self.__nombre}' "
                      f"| tarifa base: ${self.__tarifa_base:.2f}/h")
        except SoftwareFJError:
            raise
        except Exception as e:
            raise SoftwareFJError(
                f"Error inesperado al crear servicio: {e}"
            ) from e

    # ── Properties (encapsulación) ─────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, nuevo_valor: float):
        if not isinstance(nuevo_valor, (int, float)) or nuevo_valor <= 0:
            raise DatosInvalidosError(
                "Parámetro inválido 'tarifa_base': debe ser un número positivo."
            )
        self.__tarifa_base = float(nuevo_valor)
        _log.info(f"Tarifa de '{self.__nombre}' actualizada a "
                  f"${self.__tarifa_base:.2f}")

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @property
    def activo(self) -> bool:
        """Alias de `disponible` (compatibilidad con la interfaz del Gestor)."""
        return self.__disponible

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    # ── Métodos concretos de la clase base ─────────────────────────────

    def activar(self):
        self.__disponible = True
        _log.info(f"Servicio '{self.__nombre}' activado.")

    def desactivar(self):
        self.__disponible = False
        _log.warning(f"Servicio '{self.__nombre}' desactivado.")

    def verificar_disponibilidad(self):
        """Verifica que el servicio esté activo. Lanza ServicioNoDisponibleError si no."""
        if not self.__disponible:
            raise ServicioNoDisponibleError(
                f"Servicio {self.__nombre!r} está desactivado."
            )

    def _registrar_calculo(self, costo: float, detalle: str):
        """Registra internamente cada cálculo de costo (uso interno de subclases)."""
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "costo": costo,
            "detalle": detalle,
        }
        self._historial_costos.append(entrada)
        _log.debug(f"[{self.__nombre}] Costo calculado: ${costo:.2f} | {detalle}")

    def obtener_historial_costos(self) -> list:
        return list(self._historial_costos)

    def __str__(self) -> str:
        estado = "Disponible" if self.__disponible else "No disponible"
        return (f"[{self.__class__.__name__}] {self.__nombre} | "
                f"Tarifa: ${self.__tarifa_base:.2f}/h | {estado}")

    # ── Métodos abstractos (DEBEN implementarse en cada subclase) ──────

    @abstractmethod
    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        ABSTRACTO + SOBRECARGA: calcula el costo total del servicio.

        Parámetros opcionales simulan sobrecarga:
            calcular_costo(duracion)
            calcular_costo(duracion, impuesto)
            calcular_costo(duracion, impuesto, descuento)
            calcular_costo(duracion, impuesto, descuento, cliente_premium)
        """

    @abstractmethod
    def describir(self) -> str:
        """ABSTRACTO + POLIMORFISMO: descripción detallada del servicio."""

    @abstractmethod
    def validar_parametros(self, duracion_horas: float, **kwargs) -> bool:
        """ABSTRACTO: valida los parámetros antes de procesar una reserva."""

    def validar(self) -> None:
        """Confirma la integridad del servicio (heredado de EntidadBase)."""
        if self.__tarifa_base <= 0:
            raise DatosInvalidosError(
                f"Tarifa base inválida: {self.__tarifa_base}"
            )

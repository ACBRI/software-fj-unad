"""
AlquilerEquipo — servicio especializado para alquiler de equipos tecnológicos.

Implementación original: Hernán David Olaya Martínez (issue #3, rama feat/servicios)
Integración con el núcleo del sistema: Andrés Camilo Briñez Núñez

Tipos de equipo: laptop, servidor, proyector, tablet, router.
Incluye cargo adicional por seguro y depreciación según tipo.
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


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos de Software FJ."""

    TIPOS_VALIDOS = {"laptop", "servidor", "proyector", "tablet", "router"}
    DURACION_MINIMA = 2.0    # Mínimo 2 horas
    DURACION_MAXIMA = 72.0   # Máximo 72 horas (3 días)

    FACTOR_TIPO = {
        "laptop":    1.0,
        "tablet":    0.9,
        "proyector": 0.8,
        "router":    0.7,
        "servidor":  1.5,
    }

    def __init__(self, equipo_id: str, tipo_equipo: str,
                 tarifa_base: float, incluye_seguro: bool = True):
        try:
            tipo_lower = (tipo_equipo.lower().strip()
                          if isinstance(tipo_equipo, str) else "")
            if tipo_lower not in self.TIPOS_VALIDOS:
                raise DatosInvalidosError(
                    f"Parámetro inválido 'tipo_equipo': debe ser uno de "
                    f"{', '.join(sorted(self.TIPOS_VALIDOS))}."
                )
            if not equipo_id or not isinstance(equipo_id, str):
                raise DatosInvalidosError(
                    "Parámetro inválido 'equipo_id': identificador inválido."
                )

            nombre = f"Equipo {equipo_id} ({tipo_lower})"
            super().__init__(nombre, tarifa_base,
                             "Alquiler de equipo tecnológico")

            self.__equipo_id = equipo_id.upper().strip()
            self.__tipo_equipo = tipo_lower
            self.__incluye_seguro = incluye_seguro

            _log.info(f"AlquilerEquipo '{self.__equipo_id}' creado | "
                      f"Tipo: {self.__tipo_equipo} | Seguro: {incluye_seguro}")
        except SoftwareFJError:
            raise
        except Exception as e:
            raise SoftwareFJError(
                f"Error al crear AlquilerEquipo: {e}"
            ) from e

    @property
    def equipo_id(self) -> str:
        return self.__equipo_id

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def incluye_seguro(self) -> bool:
        return self.__incluye_seguro

    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        POLIMORFISMO + SOBRECARGA: calcula el costo del alquiler.

        Lógica específica:
            - Factor de costo según tipo de equipo.
            - Cargo de seguro del 5% si aplica.
            - Descuento de volumen: >24h => -5% adicional.
            - Cliente premium: -8% adicional.
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion_horas)

            factor = self.FACTOR_TIPO.get(self.__tipo_equipo, 1.0)
            tarifa_ajustada = self.tarifa_base * factor
            costo_base = tarifa_ajustada * duracion_horas

            if self.__incluye_seguro:
                costo_base *= 1.05

            descuento_total = descuento
            if duracion_horas > 24:
                descuento_total += 0.05
            if cliente_premium:
                descuento_total += 0.08

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

            detalle = (f"Equipo {self.__equipo_id} ({self.__tipo_equipo}) | "
                       f"{duracion_horas}h | Seguro={self.__incluye_seguro} | "
                       f"Desc={descuento_total*100:.0f}% | "
                       f"IVA={tasa_impuesto*100:.0f}%")
            self._registrar_calculo(costo_final, detalle)

            return round(costo_final, 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoInconsistenteError(str(e)) from e
        finally:
            _log.debug(f"[AlquilerEquipo-{self.__equipo_id}] "
                       f"Cálculo de costo procesado.")

    def describir(self) -> str:
        factor = self.FACTOR_TIPO.get(self.__tipo_equipo, 1.0)
        seguro = ("Incluido (+5%)"
                  if self.__incluye_seguro else "No incluido")
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"+-- ALQUILER DE EQUIPO ----------------------+\n"
            f"  ID Equipo     : {self.__equipo_id}\n"
            f"  Tipo          : {self.__tipo_equipo.capitalize()}\n"
            f"  Tarifa base   : ${self.tarifa_base:.2f}/hora\n"
            f"  Factor tipo   : x{factor} (depreciación/riesgo)\n"
            f"  Seguro        : {seguro}\n"
            f"  Desc. volumen : -5% si > 24 horas\n"
            f"  Duración      : {self.DURACION_MINIMA}h - {self.DURACION_MAXIMA}h\n"
            f"  Estado        : {estado}\n"
            f"+--------------------------------------------+"
        )

    def validar_parametros(self, duracion_horas: float, **kwargs) -> bool:
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

            _log.debug(f"[AlquilerEquipo-{self.__equipo_id}] "
                       f"Parámetros válidos: {duracion_horas}h")
            return True
        except SoftwareFJError:
            raise
        except Exception as e:
            raise DatosInvalidosError(f"Error de validación: {e}") from e

"""
AsesoriaEspecializada — servicio especializado de asesorías técnicas o empresariales.

Implementación original: Hernán David Olaya Martínez (issue #3, rama feat/servicios)
Integración con el núcleo del sistema: Andrés Camilo Briñez Núñez

Categorías: desarrollo, arquitectura, seguridad, datos, gestion.
Tarifa diferencial según nivel del asesor (junior, senior, experto)
y modalidad (presencial, virtual).
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


class AsesoriaEspecializada(Servicio):
    """Asesorías especializadas ofrecidas por Software FJ."""

    CATEGORIAS_VALIDAS = {
        "desarrollo", "arquitectura", "seguridad", "datos", "gestion"
    }
    MODALIDADES_VALIDAS = {"presencial", "virtual"}
    DURACION_MINIMA = 0.5  # Mínimo 30 minutos
    DURACION_MAXIMA = 4.0  # Máximo 4 horas por sesión

    NIVEL_FACTOR = {
        "junior":  1.0,
        "senior":  1.5,
        "experto": 2.0,
    }

    def __init__(self, asesoria_id: str, categoria: str,
                 tarifa_base: float, nivel_asesor: str = "senior",
                 modalidad: str = "virtual"):
        try:
            cat = (categoria.lower().strip()
                   if isinstance(categoria, str) else "")
            if cat not in self.CATEGORIAS_VALIDAS:
                raise DatosInvalidosError(
                    f"Parámetro inválido 'categoria': debe ser una de "
                    f"{', '.join(sorted(self.CATEGORIAS_VALIDAS))}."
                )

            nivel = (nivel_asesor.lower().strip()
                     if isinstance(nivel_asesor, str) else "")
            if nivel not in self.NIVEL_FACTOR:
                raise DatosInvalidosError(
                    f"Parámetro inválido 'nivel_asesor': debe ser "
                    f"{', '.join(self.NIVEL_FACTOR.keys())}."
                )

            mod = (modalidad.lower().strip()
                   if isinstance(modalidad, str) else "")
            if mod not in self.MODALIDADES_VALIDAS:
                raise DatosInvalidosError(
                    f"Parámetro inválido 'modalidad': debe ser "
                    f"{', '.join(self.MODALIDADES_VALIDAS)}."
                )

            nombre = f"Asesoría {cat.capitalize()} [{asesoria_id}]"
            super().__init__(nombre, tarifa_base,
                             f"Asesoría especializada en {cat}")

            self.__asesoria_id = asesoria_id.upper().strip()
            self.__categoria = cat
            self.__nivel_asesor = nivel
            self.__modalidad = mod
            self.__sesiones_realizadas = 0

            _log.info(f"AsesoriaEspecializada '{self.__asesoria_id}' creada | "
                      f"Cat: {cat} | Nivel: {nivel} | Modalidad: {mod}")
        except SoftwareFJError:
            raise
        except Exception as e:
            raise SoftwareFJError(
                f"Error al crear AsesoriaEspecializada: {e}"
            ) from e

    @property
    def asesoria_id(self) -> str:
        return self.__asesoria_id

    @property
    def categoria(self) -> str:
        return self.__categoria

    @property
    def nivel_asesor(self) -> str:
        return self.__nivel_asesor

    @property
    def sesiones_realizadas(self) -> int:
        return self.__sesiones_realizadas

    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        POLIMORFISMO + SOBRECARGA: calcula el costo de la asesoría.

        Lógica específica:
            - Factor de tarifa según nivel del asesor.
            - Modalidad presencial: +20% sobre tarifa.
            - Cliente premium: descuento del 15%.
            - Paquete multi-sesión: si sesiones > 5, -10%.
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion_horas)

            factor_nivel = self.NIVEL_FACTOR.get(self.__nivel_asesor, 1.0)
            tarifa_ajustada = self.tarifa_base * factor_nivel

            if self.__modalidad == "presencial":
                tarifa_ajustada *= 1.20

            costo_base = tarifa_ajustada * duracion_horas

            descuento_total = descuento
            if cliente_premium:
                descuento_total += 0.15
            if self.__sesiones_realizadas > 5:
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

            detalle = (
                f"Asesoría {self.__asesoria_id} | {self.__categoria} | "
                f"Nivel={self.__nivel_asesor} | {self.__modalidad} | "
                f"{duracion_horas}h | Desc={descuento_total*100:.0f}% | "
                f"IVA={tasa_impuesto*100:.0f}%"
            )
            self._registrar_calculo(costo_final, detalle)

            self.__sesiones_realizadas += 1
            return round(costo_final, 2)
        except SoftwareFJError:
            raise
        except Exception as e:
            raise CalculoInconsistenteError(str(e)) from e
        finally:
            _log.debug(f"[AsesoriaEspecializada-{self.__asesoria_id}] "
                       f"Cálculo de costo procesado.")

    def describir(self) -> str:
        factor = self.NIVEL_FACTOR.get(self.__nivel_asesor, 1.0)
        recargo_modalidad = "(+20%)" if self.__modalidad == "presencial" else ""
        estado = "Disponible" if self.disponible else "No disponible"
        return (
            f"+-- ASESORÍA ESPECIALIZADA ------------------+\n"
            f"  ID Asesoría   : {self.__asesoria_id}\n"
            f"  Categoría     : {self.__categoria.capitalize()}\n"
            f"  Nivel asesor  : {self.__nivel_asesor.capitalize()} (x{factor} tarifa)\n"
            f"  Modalidad     : {self.__modalidad.capitalize()} {recargo_modalidad}\n"
            f"  Tarifa base   : ${self.tarifa_base:.2f}/hora\n"
            f"  Sesiones prev.: {self.__sesiones_realizadas}\n"
            f"  Desc. fidelid.: -10% si > 5 sesiones previas\n"
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

            _log.debug(f"[AsesoriaEspecializada-{self.__asesoria_id}] "
                       f"Parámetros válidos: {duracion_horas}h")
            return True
        except SoftwareFJError:
            raise
        except Exception as e:
            raise DatosInvalidosError(f"Error de validación: {e}") from e

"""
Jerarquía de excepciones personalizadas del sistema Software FJ.

Todas heredan de SoftwareFJError, lo que permite capturarlas de forma
granular (por tipo) o genérica (por raíz) sin atrapar excepciones del
intérprete por accidente.

La jerarquía soporta encadenamiento (raise ... from ...) para preservar
la causa original cuando se envuelve una excepción de bajo nivel.
"""

from __future__ import annotations


class SoftwareFJError(Exception):
    """Raíz de todas las excepciones del dominio Software FJ."""

    codigo: str = "SFJ-000"

    def __init__(self, mensaje: str, *, codigo: str | None = None) -> None:
        super().__init__(mensaje)
        if codigo is not None:
            self.codigo = codigo

    def __str__(self) -> str:
        return f"[{self.codigo}] {super().__str__()}"


class DatosInvalidosError(SoftwareFJError):
    """Datos de entrada inválidos, mal formateados o fuera de rango."""

    codigo = "SFJ-100"


class ClienteInvalidoError(DatosInvalidosError):
    """Validación fallida sobre un Cliente (cédula, email, teléfono, etc.)."""

    codigo = "SFJ-110"


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no existe o no está disponible."""

    codigo = "SFJ-200"


class ReservaInvalidaError(SoftwareFJError):
    """Intento de reserva incorrecto: fechas, duración, estado, etc."""

    codigo = "SFJ-300"


class CalculoInconsistenteError(SoftwareFJError):
    """Un cálculo (costo, descuento, impuesto) produjo un resultado inválido."""

    codigo = "SFJ-400"


class OperacionNoPermitidaError(SoftwareFJError):
    """Se intentó ejecutar una operación prohibida por el estado actual."""

    codigo = "SFJ-500"

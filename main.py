"""
Punto de entrada de Software FJ.

Ejecuta la batería completa de simulaciones y deja constancia
en consola y en logs/sistema.log.
"""

from __future__ import annotations

from src.core.logger import obtener_logger
from src.simulaciones.escenarios import ejecutar_todos

_log = obtener_logger("main")


def main() -> None:
    _log.info("Iniciando Software FJ — Sistema Integral de Gestión")
    try:
        gestor = ejecutar_todos()
    except Exception as exc:
        _log.critical("Falla fatal durante la simulación: %s", exc, exc_info=True)
        raise
    else:
        _log.info("Resumen final: %s", gestor.resumen())
    finally:
        _log.info("Fin de ejecución.")


if __name__ == "__main__":
    main()

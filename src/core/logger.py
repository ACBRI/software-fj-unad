"""
Sistema centralizado de logging para Software FJ.

Registra simultáneamente en consola y en archivo rotativo
(logs/sistema.log). Cada módulo obtiene su propio logger nombrado
mediante obtener_logger(__name__), preservando la jerarquía.

La configuración se ejecuta una sola vez (idempotente): múltiples
llamadas a obtener_logger no duplican handlers.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_RAIZ = "software_fj"
_FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_FECHA = "%Y-%m-%d %H:%M:%S"
_RUTA_LOGS = Path(__file__).resolve().parents[2] / "logs"
_ARCHIVO_LOG = _RUTA_LOGS / "sistema.log"
_configurado = False


def _configurar_una_vez() -> None:
    """Monta handlers de consola y archivo sobre el logger raíz del sistema."""
    global _configurado
    if _configurado:
        return

    _RUTA_LOGS.mkdir(parents=True, exist_ok=True)

    logger_raiz = logging.getLogger(_RAIZ)
    logger_raiz.setLevel(logging.DEBUG)
    logger_raiz.propagate = False

    formato = logging.Formatter(_FORMATO, datefmt=_FECHA)

    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)

    handler_archivo = RotatingFileHandler(
        _ARCHIVO_LOG,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    logger_raiz.addHandler(handler_consola)
    logger_raiz.addHandler(handler_archivo)

    _configurado = True


def obtener_logger(nombre: str) -> logging.Logger:
    """Devuelve un logger hijo bajo el namespace software_fj.*."""
    _configurar_una_vez()
    return logging.getLogger(f"{_RAIZ}.{nombre}")

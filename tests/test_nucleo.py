"""Tests del núcleo: excepciones, entidad base y logger."""

from __future__ import annotations

import unittest

from src.core.entidad_base import EntidadBase
from src.core.excepciones import (
    ClienteInvalidoError,
    DatosInvalidosError,
    SoftwareFJError,
)
from src.core.logger import obtener_logger


class _EntidadDummy(EntidadBase):
    def describir(self) -> str:
        return "dummy"

    def validar(self) -> None:
        return None


class TestExcepciones(unittest.TestCase):
    def test_jerarquia(self) -> None:
        self.assertTrue(issubclass(ClienteInvalidoError, DatosInvalidosError))
        self.assertTrue(issubclass(DatosInvalidosError, SoftwareFJError))

    def test_codigo_por_defecto(self) -> None:
        error = ClienteInvalidoError("cédula inválida")
        self.assertEqual(error.codigo, "SFJ-110")
        self.assertIn("SFJ-110", str(error))

    def test_encadenamiento(self) -> None:
        try:
            try:
                raise ValueError("original")
            except ValueError as causa:
                raise ClienteInvalidoError("envuelta") from causa
        except ClienteInvalidoError as error:
            self.assertIsInstance(error.__cause__, ValueError)


class TestEntidadBase(unittest.TestCase):
    def test_identificador_autogenerado(self) -> None:
        a = _EntidadDummy()
        b = _EntidadDummy()
        self.assertNotEqual(a.identificador, b.identificador)

    def test_identificador_vacio_rechazado(self) -> None:
        with self.assertRaises(DatosInvalidosError):
            _EntidadDummy(identificador="   ")

    def test_igualdad_por_id(self) -> None:
        a = _EntidadDummy(identificador="abc")
        b = _EntidadDummy(identificador="abc")
        self.assertEqual(a, b)


class TestLogger(unittest.TestCase):
    def test_namespace_correcto(self) -> None:
        log = obtener_logger("modulo.x")
        self.assertEqual(log.name, "software_fj.modulo.x")

    def test_configuracion_idempotente(self) -> None:
        log1 = obtener_logger("a")
        log2 = obtener_logger("a")
        self.assertIs(log1, log2)


if __name__ == "__main__":
    unittest.main()

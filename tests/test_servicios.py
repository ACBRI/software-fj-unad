"""
Pruebas del módulo de Servicios (#3).

Convertidas desde la demostración manual de Hernán David Olaya Martínez
(función demostrar_modulo_servicios) a unittest, conservando todos los
casos válidos e inválidos del autor original.
"""

from __future__ import annotations

import unittest

from src.core.excepciones import (
    DatosInvalidosError,
    ServicioNoDisponibleError,
    SoftwareFJError,
)
from src.servicios_especializados.alquiler_equipo import AlquilerEquipo
from src.servicios_especializados.asesoria_especializada import AsesoriaEspecializada
from src.servicios_especializados.reserva_sala import ReservaSala


class TestServicios(unittest.TestCase):
    """Pruebas de creación y polimorfismo de los 3 servicios especializados."""

    def setUp(self):
        self.sala = ReservaSala("SALA-A1", capacidad_maxima=10,
                                tarifa_base=50.0, equipada=True)
        self.equipo = AlquilerEquipo("EQ-001", tipo_equipo="laptop",
                                     tarifa_base=20.0, incluye_seguro=True)
        self.asesoria = AsesoriaEspecializada("ASE-001", categoria="seguridad",
                                              tarifa_base=80.0,
                                              nivel_asesor="experto",
                                              modalidad="presencial")

    def test_creacion_servicios_validos(self):
        """Los 3 servicios se crean correctamente."""
        self.assertEqual(self.sala.sala_id, "SALA-A1")
        self.assertEqual(self.equipo.tipo_equipo, "laptop")
        self.assertEqual(self.asesoria.nivel_asesor, "experto")

    def test_polimorfismo_describir(self):
        """describir() devuelve representaciones distintas según el tipo."""
        for servicio in [self.sala, self.equipo, self.asesoria]:
            descripcion = servicio.describir()
            self.assertIsInstance(descripcion, str)
            self.assertIn("Tarifa base", descripcion)

    def test_sobrecarga_calcular_costo(self):
        """calcular_costo acepta múltiples combinaciones de parámetros."""
        c1 = self.sala.calcular_costo(3)
        c2 = self.equipo.calcular_costo(10, impuesto=0.10)
        c3 = self.asesoria.calcular_costo(2, descuento=0.05, cliente_premium=True)
        c4 = self.sala.calcular_costo(4, impuesto=0.19,
                                      descuento=0.10, cliente_premium=True)
        for costo in (c1, c2, c3, c4):
            self.assertGreater(costo, 0)


class TestExcepciones(unittest.TestCase):
    """Validaciones que deben lanzar excepciones del dominio (jerarquía SoftwareFJError)."""

    def test_tipo_equipo_invalido(self):
        with self.assertRaises(SoftwareFJError):
            AlquilerEquipo("EQ-BAD", tipo_equipo="avion", tarifa_base=10.0)

    def test_duracion_fuera_de_rango(self):
        sala = ReservaSala("SALA-R", capacidad_maxima=5, tarifa_base=30.0)
        with self.assertRaises(DatosInvalidosError):
            sala.calcular_costo(12)  # excede DURACION_MAXIMA=8

    def test_servicio_desactivado(self):
        equipo = AlquilerEquipo("EQ-R", tipo_equipo="tablet", tarifa_base=15.0)
        equipo.desactivar()
        with self.assertRaises(ServicioNoDisponibleError):
            equipo.calcular_costo(5)

    def test_tarifa_negativa(self):
        sala = ReservaSala("SALA-R2", capacidad_maxima=5, tarifa_base=30.0)
        with self.assertRaises(DatosInvalidosError):
            sala.tarifa_base = -100

    def test_categoria_asesoria_invalida(self):
        with self.assertRaises(SoftwareFJError):
            AsesoriaEspecializada("ASE-X", categoria="cocina",
                                  tarifa_base=50.0)


class TestHistorialCostos(unittest.TestCase):
    """El historial interno registra cada cálculo realizado."""

    def test_historial_se_acumula(self):
        sala = ReservaSala("SALA-H", capacidad_maxima=8, tarifa_base=40.0)
        sala.calcular_costo(2)
        sala.calcular_costo(3)
        historial = sala.obtener_historial_costos()
        self.assertEqual(len(historial), 2)
        for entrada in historial:
            self.assertIn("timestamp", entrada)
            self.assertIn("costo", entrada)


if __name__ == "__main__":
    unittest.main()

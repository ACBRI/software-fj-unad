"""
Pruebas del módulo de Reservas (#4).

Convertidas desde la demostración manual de Hernán David Olaya Martínez
(función demostrar_modulo_reservas) a unittest, conservando los casos
válidos e inválidos del autor original.
"""

from __future__ import annotations

import unittest

from src.core.excepciones import (
    OperacionNoPermitidaError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from src.modelos.cliente import Cliente
from src.modelos.reserva import EstadoReserva, Reserva
from src.modelos.servicio import Servicio


class _ServicioFalso(Servicio):
    """Implementación mínima de Servicio para tests unitarios."""

    def __init__(self, nombre="Test", tarifa=100.0):
        super().__init__(nombre, tarifa)

    def calcular_costo(self, horas, *, impuesto=0.19, descuento=0.0):
        return round(self._tarifa_base * horas * (1 - descuento) * (1 + impuesto), 2)

    def describir(self):
        return f"ServicioFalso({self.nombre})"


def _cliente_demo(cedula="1023456789", nombre="Ana Torres",
                  email="ana@example.com", telefono="3001234567"):
    return Cliente(cedula, nombre, email, telefono)


class TestCreacionReserva(unittest.TestCase):
    def setUp(self):
        self.cliente = _cliente_demo()
        self.servicio = _ServicioFalso()

    def test_reserva_valida(self):
        reserva = Reserva(self.cliente, self.servicio, horas=3)
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)
        self.assertEqual(reserva.horas, 3)

    def test_duracion_invalida(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.cliente, self.servicio, horas=0)
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.cliente, self.servicio, horas=-2)

    def test_cliente_no_es_cliente(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva("no-es-cliente", self.servicio, horas=3)

    def test_servicio_no_es_servicio(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva(self.cliente, "no-es-servicio", horas=3)

    def test_reserva_id_explicito(self):
        reserva = Reserva(self.cliente, self.servicio, horas=2, reserva_id="RES-X1")
        self.assertEqual(reserva.identificador, "RES-X1")


class TestTransicionesEstado(unittest.TestCase):
    def setUp(self):
        self.cliente = _cliente_demo()
        self.servicio = _ServicioFalso()
        self.reserva = Reserva(self.cliente, self.servicio, horas=2)

    def test_confirmar_calcula_costo(self):
        costo = self.reserva.confirmar()
        self.assertGreater(costo, 0)
        self.assertEqual(self.reserva.estado, EstadoReserva.CONFIRMADA)

    def test_confirmar_dos_veces_falla(self):
        self.reserva.confirmar()
        with self.assertRaises(OperacionNoPermitidaError):
            self.reserva.confirmar()

    def test_cancelar_pendiente_sin_cargo(self):
        resultado = self.reserva.cancelar("test")
        self.assertEqual(resultado["cargo_cancelacion"], 0.0)
        self.assertEqual(self.reserva.estado, EstadoReserva.CANCELADA)

    def test_cancelar_confirmada_aplica_cargo(self):
        self.reserva.confirmar()
        resultado = self.reserva.cancelar("test")
        self.assertGreater(resultado["cargo_cancelacion"], 0)

    def test_no_cancelar_procesada(self):
        self.reserva.confirmar()
        self.reserva.procesar_pago(self.reserva.costo_total)
        with self.assertRaises(OperacionNoPermitidaError):
            self.reserva.cancelar()

    def test_procesar_atajo_deja_estado_procesada(self):
        costo = self.reserva.procesar()
        self.assertGreater(costo, 0)
        self.assertEqual(self.reserva.estado, EstadoReserva.PROCESADA)

    def test_completar_explicito_marca_completada(self):
        self.reserva.procesar()
        self.reserva.completar()
        self.assertEqual(self.reserva.estado, EstadoReserva.COMPLETADA)


class TestSobrecargaPago(unittest.TestCase):
    def setUp(self):
        self.cliente = _cliente_demo()
        self.servicio = _ServicioFalso()
        self.reserva = Reserva(self.cliente, self.servicio, horas=2)
        self.reserva.confirmar()

    def test_pago_efectivo(self):
        comp = self.reserva.procesar_pago(self.reserva.costo_total)
        self.assertEqual(comp["metodo_pago"], "efectivo")

    def test_pago_tarjeta_cuotas(self):
        comp = self.reserva.procesar_pago(
            self.reserva.costo_total,
            metodo_pago="tarjeta",
            cuotas=3,
        )
        self.assertEqual(comp["cuotas"], 3)
        self.assertGreater(comp["cargo_cuotas"], 0)

    def test_pago_metodo_invalido(self):
        with self.assertRaises(SoftwareFJError):
            self.reserva.procesar_pago(self.reserva.costo_total, metodo_pago="bitcoin")

    def test_cuotas_solo_con_tarjeta(self):
        with self.assertRaises(SoftwareFJError):
            self.reserva.procesar_pago(
                self.reserva.costo_total,
                metodo_pago="efectivo",
                cuotas=3,
            )

    def test_pago_insuficiente(self):
        with self.assertRaises(SoftwareFJError):
            self.reserva.procesar_pago(monto=1.0)


if __name__ == "__main__":
    unittest.main()

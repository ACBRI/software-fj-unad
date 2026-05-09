# Autor: Wilmer Garcia Ochoa
# Programación
# Programa: Clase reserva con estados y métodos sobrecargados.

# Descripción: La clase Reserva permite gestionar las reservas del sistema integrando cliente, servicio, duración y estado.
# Incluye métodos para confirmar, cancelar y procesar reservas, además de un método sobrecargado para calcular el costo total con parámetros opcionales como impuestos y descuentos.
# También incorpora validaciones y manejo de excepciones para garantizar un funcionamiento estable y controlado.

# ==========================================
# Clase Reserva
# Programación - Fase 4
# ==========================================


class ErrorReserva(Exception):
    """Excepción personalizada para errores de reserva."""
    pass


class Reserva:
    """
    Representa una reserva dentro del sistema.

    Atributos:
        cliente
        servicio
        duracion
        estado
    """

    ESTADOS_VALIDOS = (
        "pendiente",
        "confirmada",
        "cancelada",
        "procesada"
    )

    def __init__(self, cliente, servicio, duracion):
        """
        Inicializa una reserva.
        """

        if cliente is None:
            raise ErrorReserva(
                "El cliente no puede ser nulo."
            )

        if servicio is None:
            raise ErrorReserva(
                "El servicio no puede ser nulo."
            )

        if duracion <= 0:
            raise ErrorReserva(
                "La duración debe ser mayor que cero."
            )

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "pendiente"

    def confirmar(self):
        """
        Cambia el estado a confirmada.
        """

        if self.estado == "cancelada":
            raise ErrorReserva(
                "No se puede confirmar una reserva cancelada."
            )

        if self.estado == "procesada":
            raise ErrorReserva(
                "La reserva ya fue procesada."
            )

        self.estado = "confirmada"

    def cancelar(self):
        """
        Cambia el estado a cancelada.
        """

        if self.estado == "procesada":
            raise ErrorReserva(
                "No se puede cancelar una reserva procesada."
            )

        self.estado = "cancelada"

    def procesar(self):
        """
        Procesa la reserva.
        """

        if self.estado != "confirmada":
            raise ErrorReserva(
                "Solo se pueden procesar reservas confirmadas."
            )

        self.estado = "procesada"

    def calcular_total(self, impuesto=0, descuento=0):
        """
        Método sobrecargado usando parámetros opcionales.

        Permite calcular el total:
        - normal
        - con impuesto
        - con descuento
        """

        try:
            costo_base = self.servicio.calcular_costo(
                self.duracion
            )

            total = costo_base + impuesto - descuento

            if total < 0:
                raise ErrorReserva(
                    "El total no puede ser negativo."
                )

            return total

        except AttributeError as e:
            raise ErrorReserva(
                "El servicio no implementa calcular_costo()."
            ) from e

    def mostrar(self):
        """
        Muestra los datos principales de la reserva.
        """

        print("Cliente:", self.cliente.nombre)
        print("Servicio:", self.servicio.nombre)
        print("Duración:", self.duracion)
        print("Estado:", self.estado)
# Autor: Wilmer Garcia Ochoa
# Programación
# Programa: Clase reserva con estados y métodos sobrecargados.
# Pruebas Reserva

from reserva import Reserva, ErrorReserva


class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre


class Servicio:
    def __init__(self, nombre, tarifa):
        self.nombre = nombre
        self.tarifa = tarifa

    def calcular_costo(self, duracion):
        return self.tarifa * duracion


def ejecutar_prueba(numero, funcion):
    print("\n==========================")
    print("OPERACIÓN", numero)
    print("==========================")

    try:
        funcion()

    except Exception as e:
        print("Error:", e)


# 1
def prueba_1():
    cliente = Cliente("Ana")
    servicio = Servicio("Sala", 50)
    reserva = Reserva(cliente, servicio, 2)
    reserva.mostrar()


# 2
def prueba_2():
    cliente = Cliente("Luis")
    servicio = Servicio("Equipo", 40)
    reserva = Reserva(cliente, servicio, 3)
    reserva.confirmar()
    reserva.mostrar()


# 3
def prueba_3():
    cliente = Cliente("Carlos")
    servicio = Servicio("Asesoría", 100)
    reserva = Reserva(cliente, servicio, 1)
    reserva.confirmar()
    reserva.procesar()
    reserva.mostrar()


# 4
def prueba_4():
    cliente = Cliente("María")
    servicio = Servicio("Sala", 30)
    reserva = Reserva(cliente, servicio, 4)
    print("Total:", reserva.calcular_total())


# 5
def prueba_5():
    cliente = Cliente("Pedro")
    servicio = Servicio("Equipo", 20)
    reserva = Reserva(cliente, servicio, 5)
    print(
        "Total con impuesto:",
        reserva.calcular_total(impuesto=10)
    )


# 6
def prueba_6():
    cliente = Cliente("Laura")
    servicio = Servicio("Asesoría", 80)
    reserva = Reserva(cliente, servicio, 2)
    print(
        "Total con descuento:",
        reserva.calcular_total(descuento=15)
    )


# 7
def prueba_7():
    cliente = Cliente("Sara")
    servicio = Servicio("Sala", 40)
    Reserva(cliente, servicio, 0)


# 8
def prueba_8():
    cliente = Cliente("Andrés")
    servicio = Servicio("Equipo", 25)
    reserva = Reserva(cliente, servicio, 2)
    reserva.procesar()


# 9
def prueba_9():
    cliente = Cliente("Camila")
    servicio = Servicio("Asesoría", 90)
    reserva = Reserva(cliente, servicio, 1)
    reserva.cancelar()
    reserva.confirmar()


# 10
def prueba_10():
    cliente = Cliente("Jorge")
    servicio = Servicio("Sala", 10)
    reserva = Reserva(cliente, servicio, 1)
    print(
        "Total:",
        reserva.calcular_total(descuento=50)
    )


pruebas = [
    prueba_1,
    prueba_2,
    prueba_3,
    prueba_4,
    prueba_5,
    prueba_6,
    prueba_7,
    prueba_8,
    prueba_9,
    prueba_10
]


for i, prueba in enumerate(pruebas, start=1):
    ejecutar_prueba(i, prueba)
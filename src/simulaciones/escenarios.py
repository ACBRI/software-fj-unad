"""
Escenarios de simulación — 10+ operaciones válidas e inválidas.

Responsable principal: John Alexander Gaitán Barrera (issue #5)
Implementación inicial provista por el líder para garantizar el flujo
end-to-end; se espera ampliación con más casos límite y documentación.

Cada escenario se ejecuta dentro de un try/except aislado, de modo que
una falla en uno NO detiene los siguientes. Este es el corazón de la
demostración de robustez exigida por la rúbrica.
"""

from __future__ import annotations

from src.core.excepciones import SoftwareFJError
from src.core.logger import obtener_logger
from src.modelos.cliente import Cliente
from src.servicios_especializados.alquiler_equipo import AlquilerEquipo
from src.servicios_especializados.asesoria_especializada import AsesoriaEspecializada
from src.servicios_especializados.gestor import GestorSistema
from src.servicios_especializados.reserva_sala import ReservaSala

_log = obtener_logger(__name__)


def _ejecutar(nombre: str, accion) -> None:
    """Ejecuta un escenario aislando sus excepciones."""
    _log.info("=" * 60)
    _log.info("▶ Escenario: %s", nombre)
    try:
        accion()
    except SoftwareFJError as error:
        _log.warning("Escenario '%s' terminó con excepción controlada: %s", nombre, error)
    except Exception as exc:
        _log.critical(
            "Escenario '%s' lanzó excepción INESPERADA: %s", nombre, exc, exc_info=True
        )


def ejecutar_todos() -> GestorSistema:
    """Corre los 10+ escenarios y devuelve el gestor con el estado final."""
    gestor = GestorSistema()

    sala = ReservaSala("Sala Andes", tarifa_base=40_000, capacidad=12)
    proyector = AlquilerEquipo("Proyector 4K", tarifa_base=25_000, tipo_equipo="Proyector")
    asesoria = AsesoriaEspecializada("Consultoría Cloud", tarifa_base=120_000, area="DevOps")

    _ejecutar("1. Registro de servicios válidos", lambda: (
        gestor.registrar_servicio(sala),
        gestor.registrar_servicio(proyector),
        gestor.registrar_servicio(asesoria),
    ))

    cliente_ok = Cliente("1023456789", "Ana Torres", "ana@example.com", "3001234567")
    _ejecutar("2. Registro de cliente válido", lambda: gestor.registrar_cliente(cliente_ok))

    _ejecutar("3. Registro de cliente con email inválido", lambda: gestor.registrar_cliente(
        Cliente("1099887766", "Luis Pérez", "correo-sin-arroba", "3117654321")
    ))

    _ejecutar("4. Registro duplicado por cédula", lambda: gestor.registrar_cliente(
        Cliente("1023456789", "Ana Torres Dup", "ana2@example.com", "3001112222")
    ))

    cliente_2 = Cliente("1055443322", "Carlos Ruiz", "carlos@example.com", "3201112233")
    _ejecutar("5. Registro de segundo cliente válido", lambda: gestor.registrar_cliente(cliente_2))

    reserva_ok = None

    def _crear_reserva_ok():
        nonlocal reserva_ok
        reserva_ok = gestor.crear_reserva(cliente_ok, sala, horas=3)

    _ejecutar("6. Creación de reserva válida (sala 3h)", _crear_reserva_ok)

    _ejecutar("7. Reserva con duración inválida", lambda: gestor.crear_reserva(
        cliente_ok, proyector, horas=0
    ))

    _ejecutar("8. Procesar reserva confirmada", lambda: gestor.procesar_reserva(reserva_ok))

    _ejecutar(
        "9. Reintento de procesar reserva ya procesada",
        lambda: gestor.procesar_reserva(reserva_ok),
    )

    reserva_cancelada = gestor.crear_reserva(cliente_2, asesoria, horas=12)
    reserva_cancelada.cancelar()
    _ejecutar(
        "10. Procesar reserva cancelada (debe fallar controladamente)",
        lambda: gestor.procesar_reserva(reserva_cancelada),
    )

    _ejecutar("11. Servicio desactivado → reserva debe fallar", lambda: (
        proyector.desactivar(),
        gestor.crear_reserva(cliente_2, proyector, horas=2),
    ))

    _ejecutar("12. Cálculo con descuento inválido (>100%)", lambda: sala.calcular_costo(
        horas=2, descuento=1.5
    ))

    _log.info("=" * 60)
    _log.info("✔ Simulación completa. %s", gestor.resumen())
    return gestor

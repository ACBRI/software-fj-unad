"""
=============================================================
Universidad Nacional Abierta y a Distancia - UNAD
Curso: Programación - Código: 213023
Fase 4 - Prácticas Simuladas

Módulo 3: Clase abstracta Servicio + Servicios Especializados
Empresa: Software FJ

Integrante: Hernán David Olaya Martínez
Rama GitHub: feat/servicios
Issue: #3
=============================================================

CONCEPTOS APLICADOS:
    - Abstracción: clase abstracta Servicio con métodos abstractos
    - Herencia: ReservaSala, AlquilerEquipo, AsesoriEspecializada
      heredan de Servicio
    - Polimorfismo: cada servicio sobrescribe calcular_costo(),
      describir() y validar_parametros()
    - Sobrecarga: calcular_costo() acepta parámetros opcionales
      (impuesto, descuento, cliente_premium)
    - Encapsulación: atributos privados con getters/setters
    - Manejo de excepciones: try/except, try/except/else,
      try/except/finally, excepciones personalizadas,
      encadenamiento de excepciones
"""

from abc import ABC, abstractmethod
import logging
import os
from datetime import datetime


# =============================================================
# CONFIGURACIÓN DE LOGGING
# Registra eventos y errores en archivo + consola
# =============================================================
def configurar_logger(nombre: str) -> logging.Logger:
    """
    Configura un logger que escribe en consola y en archivo de log.

    Args:
        nombre (str): Nombre del módulo para identificar el logger

    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(nombre)
    logger.setLevel(logging.DEBUG)

    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger

    # Formato de los mensajes de log
    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    console_handler.setLevel(logging.INFO)

    # Handler de archivo (crea o añade al archivo de logs del sistema)
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/software_fj.log", encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


# Logger del módulo de servicios
logger = configurar_logger("SFJ.servicios")


# =============================================================
# EXCEPCIONES PERSONALIZADAS DEL MÓDULO
# Siguen la convención de códigos SFJ-XXX del proyecto
# =============================================================

class ServicioError(Exception):
    """
    Excepción base para todos los errores del módulo de servicios.
    Incluye un código trazable con prefijo SFJ-3XX.
    """
    def __init__(self, mensaje: str, codigo: str = "SFJ-300"):
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(f"[{codigo}] {mensaje}")
        # Registra el error automáticamente en el log
        logger.error(f"[{codigo}] {mensaje}")


class ServicioNoDisponibleError(ServicioError):
    """Error cuando el servicio está inactivo o no puede prestarse."""
    def __init__(self, nombre_servicio: str):
        super().__init__(
            f"El servicio '{nombre_servicio}' no está disponible actualmente.",
            codigo="SFJ-301"
        )


class ParametroInvalidoError(ServicioError):
    """Error cuando un parámetro requerido es inválido o faltante."""
    def __init__(self, parametro: str, razon: str):
        super().__init__(
            f"Parámetro inválido '{parametro}': {razon}",
            codigo="SFJ-302"
        )


class CapacidadExcedidaError(ServicioError):
    """Error cuando se supera la capacidad máxima del servicio."""
    def __init__(self, servicio: str, maximo: int, solicitado: int):
        super().__init__(
            f"Servicio '{servicio}': capacidad máxima {maximo}, "
            f"solicitada {solicitado}.",
            codigo="SFJ-303"
        )


class CostoInvalidoError(ServicioError):
    """Error cuando el cálculo de costo produce un resultado inválido."""
    def __init__(self, detalle: str):
        super().__init__(
            f"Error en cálculo de costo: {detalle}",
            codigo="SFJ-304"
        )


class DuracionInvalidaError(ServicioError):
    """Error cuando la duración solicitada está fuera del rango permitido."""
    def __init__(self, minimo: float, maximo: float, recibida: float):
        super().__init__(
            f"Duración {recibida}h fuera del rango permitido "
            f"[{minimo}h – {maximo}h].",
            codigo="SFJ-305"
        )


# =============================================================
# CLASE ABSTRACTA BASE: Servicio
# Define la interfaz común para todos los servicios de Software FJ
# =============================================================

class Servicio(ABC):
    """
    CLASE ABSTRACTA que representa un servicio genérico de Software FJ.

    ABSTRACCIÓN: define métodos abstractos que OBLIGAN a cada servicio
    especializado a implementar su propia lógica.

    ENCAPSULACIÓN: atributos privados (_nombre, _tarifa_base, _disponible)
    con acceso mediante properties.

    Subclases concretas:
        - ReservaSala
        - AlquilerEquipo
        - AsesoriaEspecializada
    """

    # Impuesto general de la empresa (19% IVA)
    IVA_GENERAL = 0.19

    def __init__(self, nombre: str, tarifa_base: float,
                 descripcion_breve: str = ""):
        """
        Constructor de la clase abstracta.

        Args:
            nombre (str): Nombre identificador del servicio
            tarifa_base (float): Precio base por hora o unidad
            descripcion_breve (str): Descripción corta del servicio
        """
        try:
            # Validaciones en el constructor
            if not nombre or not isinstance(nombre, str):
                raise ParametroInvalidoError("nombre",
                                             "debe ser una cadena no vacía")
            if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
                raise ParametroInvalidoError("tarifa_base",
                                             "debe ser un número positivo")

            # Atributos privados (encapsulación)
            self.__nombre = nombre.strip()
            self.__tarifa_base = float(tarifa_base)
            self.__descripcion_breve = descripcion_breve
            self.__disponible = True           # Estado del servicio
            self.__fecha_creacion = datetime.now()
            self._historial_costos = []        # Registro interno de cálculos

            logger.info(f"Servicio creado: '{self.__nombre}' "
                        f"| tarifa base: ${self.__tarifa_base:.2f}/h")

        except ServicioError:
            # Ya fue registrado en el logger por la excepción personalizada
            raise
        except Exception as e:
            # Encadenamiento de excepciones: convierte error inesperado
            raise ServicioError(
                f"Error inesperado al crear servicio: {e}",
                "SFJ-300"
            ) from e

    # ── Properties (encapsulación: acceso controlado) ──────────────────

    @property
    def nombre(self) -> str:
        """Retorna el nombre del servicio (solo lectura)."""
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base del servicio."""
        return self.__tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, nuevo_valor: float):
        """Permite actualizar la tarifa con validación."""
        try:
            if not isinstance(nuevo_valor, (int, float)) or nuevo_valor <= 0:
                raise ParametroInvalidoError("tarifa_base",
                                             "debe ser un número positivo")
            self.__tarifa_base = float(nuevo_valor)
            logger.info(f"Tarifa de '{self.__nombre}' actualizada a "
                        f"${self.__tarifa_base:.2f}")
        except ServicioError:
            raise

    @property
    def disponible(self) -> bool:
        """Indica si el servicio está activo."""
        return self.__disponible

    @property
    def fecha_creacion(self) -> datetime:
        """Retorna la fecha de creación del servicio."""
        return self.__fecha_creacion

    # ── Métodos concretos de la clase base ─────────────────────────────

    def activar(self):
        """Activa el servicio para que pueda recibir reservas."""
        self.__disponible = True
        logger.info(f"Servicio '{self.__nombre}' activado.")

    def desactivar(self):
        """Desactiva el servicio; no aceptará nuevas reservas."""
        self.__disponible = False
        logger.warning(f"Servicio '{self.__nombre}' desactivado.")

    def verificar_disponibilidad(self):
        """
        Verifica que el servicio esté activo.
        Lanza ServicioNoDisponibleError si no lo está.

        Uso con try/except recomendado para el módulo de Reservas.
        """
        if not self.__disponible:
            raise ServicioNoDisponibleError(self.__nombre)

    def _registrar_calculo(self, costo: float, detalle: str):
        """
        Método protegido: registra internamente cada cálculo de costo.
        Solo accesible por subclases.

        Args:
            costo (float): Costo calculado
            detalle (str): Descripción del cálculo
        """
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "costo": costo,
            "detalle": detalle
        }
        self._historial_costos.append(entrada)
        logger.debug(f"[{self.__nombre}] Costo calculado: ${costo:.2f} | {detalle}")

    def obtener_historial_costos(self) -> list:
        """Retorna el historial de cálculos de costo del servicio."""
        return list(self._historial_costos)

    def __str__(self) -> str:
        """Representación legible del servicio."""
        estado = "✅ Disponible" if self.__disponible else "❌ No disponible"
        return (f"[{self.__class__.__name__}] {self.__nombre} | "
                f"Tarifa: ${self.__tarifa_base:.2f}/h | {estado}")

    # ── Métodos abstractos (DEBEN implementarse en cada subclase) ──────

    @abstractmethod
    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        ABSTRACTO - SOBRECARGA: calcula el costo total del servicio.

        Parámetros opcionales simulan sobrecarga:
            calcular_costo(duracion)
            calcular_costo(duracion, impuesto)
            calcular_costo(duracion, impuesto, descuento)
            calcular_costo(duracion, impuesto, descuento, cliente_premium)

        Args:
            duracion_horas (float): Horas de uso del servicio
            impuesto (float): Tasa de impuesto (None = usa IVA general)
            descuento (float): Porcentaje de descuento (0.0 – 1.0)
            cliente_premium (bool): Si True, aplica descuento adicional

        Returns:
            float: Costo total calculado
        """
        pass

    @abstractmethod
    def describir(self) -> str:
        """
        ABSTRACTO - POLIMORFISMO: retorna una descripción detallada
        y específica de cada tipo de servicio.

        Returns:
            str: Descripción completa del servicio
        """
        pass

    @abstractmethod
    def validar_parametros(self, duracion_horas: float, **kwargs) -> bool:
        """
        ABSTRACTO: valida los parámetros antes de procesar una reserva.
        Cada servicio tiene sus propias reglas de validación.

        Args:
            duracion_horas (float): Duración solicitada
            **kwargs: Parámetros adicionales específicos de cada servicio

        Returns:
            bool: True si todos los parámetros son válidos

        Raises:
            ParametroInvalidoError, DuracionInvalidaError, etc.
        """
        pass


# =============================================================
# CLASE HIJA 1: ReservaSala
# Servicio para reservar salas de reuniones o trabajo
# =============================================================

class ReservaSala(Servicio):
    """
    HERENCIA de Servicio.
    Gestiona la reserva de salas de reuniones o trabajo en Software FJ.

    Atributos propios:
        - capacidad_maxima: máximo de personas admitidas
        - sala_id: identificador único de la sala
        - equipada: si la sala tiene proyector y equipos incluidos

    POLIMORFISMO: sobrescribe calcular_costo(), describir(),
    validar_parametros() con lógica específica de salas.
    """

    DURACION_MINIMA = 1.0    # Mínimo 1 hora
    DURACION_MAXIMA = 8.0    # Máximo 8 horas por reserva
    TARIFA_EQUIPADA = 1.3    # 30% extra si la sala está equipada

    def __init__(self, sala_id: str, capacidad_maxima: int,
                 tarifa_base: float, equipada: bool = False):
        """
        Constructor de ReservaSala.

        Args:
            sala_id (str): Identificador único de la sala (ej: "SALA-A1")
            capacidad_maxima (int): Número máximo de personas
            tarifa_base (float): Precio base por hora
            equipada (bool): True si incluye proyector y equipos
        """
        try:
            # Valida antes de llamar al constructor padre
            if not sala_id or not isinstance(sala_id, str):
                raise ParametroInvalidoError("sala_id",
                                             "debe ser un identificador válido")
            if not isinstance(capacidad_maxima, int) or capacidad_maxima < 1:
                raise ParametroInvalidoError("capacidad_maxima",
                                             "debe ser un entero positivo")

            # Llama al constructor de la clase abstracta
            nombre = f"Sala {sala_id}"
            super().__init__(nombre, tarifa_base,
                             "Reserva de sala de reuniones o trabajo")

            # Atributos propios de ReservaSala
            self.__sala_id = sala_id.upper().strip()
            self.__capacidad_maxima = capacidad_maxima
            self.__equipada = equipada
            self.__personas_reserva = 0        # Se actualiza al reservar

            logger.info(f"ReservaSala '{self.__sala_id}' creada | "
                        f"Cap: {capacidad_maxima} personas | "
                        f"Equipada: {equipada}")

        except ServicioError:
            raise
        except Exception as e:
            raise ServicioError(
                f"Error al crear ReservaSala: {e}", "SFJ-300"
            ) from e

    @property
    def sala_id(self) -> str:
        return self.__sala_id

    @property
    def capacidad_maxima(self) -> int:
        return self.__capacidad_maxima

    @property
    def equipada(self) -> bool:
        return self.__equipada

    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        POLIMORFISMO + SOBRECARGA: calcula el costo de reservar la sala.

        Lógica específica:
            - Si la sala está equipada: +30% sobre tarifa base
            - Cliente premium: -10% adicional de descuento
            - Impuesto: usa IVA general si no se especifica

        Args:
            duracion_horas: Horas de uso (1 a 8)
            impuesto: Tasa de impuesto (None = IVA 19%)
            descuento: Descuento porcentual (0.0 a 1.0)
            cliente_premium: Si True aplica descuento extra del 10%

        Returns:
            float: Costo total con impuestos y descuentos

        Raises:
            ServicioNoDisponibleError, DuracionInvalidaError,
            CostoInvalidoError
        """
        try:
            # Verifica disponibilidad del servicio
            self.verificar_disponibilidad()

            # Valida parámetros con el método abstracto implementado
            self.validar_parametros(duracion_horas)

            # Tarifa base ajustada por tipo de sala
            tarifa = self.tarifa_base
            if self.__equipada:
                tarifa *= self.TARIFA_EQUIPADA

            # Costo base = tarifa por horas
            costo_base = tarifa * duracion_horas

            # Descuento adicional por cliente premium
            descuento_total = descuento
            if cliente_premium:
                descuento_total += 0.10   # 10% extra para premium

            # Aplicar descuento (máximo 50% para no generar costo negativo)
            descuento_total = min(descuento_total, 0.50)
            costo_con_descuento = costo_base * (1 - descuento_total)

            # Aplicar impuesto (usa IVA general si no se especifica)
            tasa_impuesto = impuesto if impuesto is not None else self.IVA_GENERAL
            if not isinstance(tasa_impuesto, (int, float)) or tasa_impuesto < 0:
                raise ParametroInvalidoError("impuesto",
                                             "debe ser un número no negativo")

            costo_final = costo_con_descuento * (1 + tasa_impuesto)

            if costo_final < 0:
                raise CostoInvalidoError(f"resultado negativo: ${costo_final:.2f}")

            # Registra el cálculo en el historial interno
            detalle = (f"Sala {self.__sala_id} | {duracion_horas}h | "
                       f"Equipada={self.__equipada} | "
                       f"Desc={descuento_total*100:.0f}% | "
                       f"IVA={tasa_impuesto*100:.0f}% | "
                       f"Premium={cliente_premium}")
            self._registrar_calculo(costo_final, detalle)

            return round(costo_final, 2)

        except ServicioError:
            raise
        except Exception as e:
            # Encadenamiento de excepciones para errores inesperados
            raise CostoInvalidoError(str(e)) from e

        finally:
            # try/finally: siempre registra el intento de cálculo
            logger.debug(f"[ReservaSala-{self.__sala_id}] "
                         f"Intento de cálculo de costo completado.")

    def describir(self) -> str:
        """
        POLIMORFISMO: descripción específica de la sala.

        Returns:
            str: Descripción detallada de la sala
        """
        equipamiento = "Proyector, pantalla, sistema de audio" \
            if self.__equipada else "Sin equipamiento adicional"
        return (
            f"╔══ RESERVA DE SALA ══════════════════════════╗\n"
            f"  ID Sala       : {self.__sala_id}\n"
            f"  Capacidad     : {self.__capacidad_maxima} personas\n"
            f"  Tarifa base   : ${self.tarifa_base:.2f}/hora\n"
            f"  Equipamiento  : {equipamiento}\n"
            f"  Extra equipada: +{(self.TARIFA_EQUIPADA-1)*100:.0f}% "
            f"sobre tarifa\n"
            f"  Duración      : {self.DURACION_MINIMA}h – "
            f"{self.DURACION_MAXIMA}h\n"
            f"  Estado        : "
            f"{'✅ Disponible' if self.disponible else '❌ No disponible'}\n"
            f"╚═════════════════════════════════════════════╝"
        )

    def validar_parametros(self, duracion_horas: float,
                           personas: int = 0, **kwargs) -> bool:
        """
        POLIMORFISMO: validaciones específicas para reserva de sala.

        Args:
            duracion_horas: Debe estar entre DURACION_MINIMA y DURACION_MAXIMA
            personas: No puede superar la capacidad máxima

        Returns:
            bool: True si todos los parámetros son válidos

        Raises:
            DuracionInvalidaError, CapacidadExcedidaError,
            ParametroInvalidoError
        """
        try:
            # Valida que la duración sea numérica
            if not isinstance(duracion_horas, (int, float)):
                raise ParametroInvalidoError("duracion_horas",
                                             "debe ser un número")

            # Valida rango de duración
            if not (self.DURACION_MINIMA <= duracion_horas
                    <= self.DURACION_MAXIMA):
                raise DuracionInvalidaError(
                    self.DURACION_MINIMA,
                    self.DURACION_MAXIMA,
                    duracion_horas
                )

            # Valida capacidad de personas si se especifica
            if personas > 0:
                if not isinstance(personas, int):
                    raise ParametroInvalidoError("personas",
                                                 "debe ser un entero")
                if personas > self.__capacidad_maxima:
                    raise CapacidadExcedidaError(
                        self.nombre,
                        self.__capacidad_maxima,
                        personas
                    )
                self.__personas_reserva = personas

            logger.debug(f"[ReservaSala-{self.__sala_id}] "
                         f"Parámetros válidos: {duracion_horas}h, "
                         f"{personas} personas")
            return True

        except ServicioError:
            raise
        except Exception as e:
            raise ParametroInvalidoError("validación",
                                         str(e)) from e


# =============================================================
# CLASE HIJA 2: AlquilerEquipo
# Servicio para el alquiler de equipos tecnológicos
# =============================================================

class AlquilerEquipo(Servicio):
    """
    HERENCIA de Servicio.
    Gestiona el alquiler de equipos tecnológicos de Software FJ.

    Tipos de equipo disponibles: laptop, servidor, proyector, tablet, router
    Incluye cargo adicional por seguro y depreciación según tipo.

    POLIMORFISMO: lógica de costo, descripción y validación propias.
    """

    TIPOS_VALIDOS = {"laptop", "servidor", "proyector", "tablet", "router"}
    DURACION_MINIMA = 2.0      # Mínimo 2 horas
    DURACION_MAXIMA = 72.0     # Máximo 72 horas (3 días)

    # Factor de costo extra por tipo de equipo (riesgo/depreciación)
    FACTOR_TIPO = {
        "laptop":    1.0,
        "tablet":    0.9,
        "proyector": 0.8,
        "router":    0.7,
        "servidor":  1.5      # Servidor tiene mayor costo por riesgo
    }

    def __init__(self, equipo_id: str, tipo_equipo: str,
                 tarifa_base: float, incluye_seguro: bool = True):
        """
        Constructor de AlquilerEquipo.

        Args:
            equipo_id (str): Identificador del equipo (ej: "EQ-001")
            tipo_equipo (str): Tipo del equipo (laptop, servidor, etc.)
            tarifa_base (float): Precio base por hora de alquiler
            incluye_seguro (bool): True si se cobra seguro adicional (5%)
        """
        try:
            tipo_lower = tipo_equipo.lower().strip() \
                if isinstance(tipo_equipo, str) else ""
            if tipo_lower not in self.TIPOS_VALIDOS:
                raise ParametroInvalidoError(
                    "tipo_equipo",
                    f"debe ser uno de: {', '.join(self.TIPOS_VALIDOS)}"
                )
            if not equipo_id or not isinstance(equipo_id, str):
                raise ParametroInvalidoError("equipo_id",
                                             "identificador inválido")

            nombre = f"Equipo {equipo_id} ({tipo_lower})"
            super().__init__(nombre, tarifa_base,
                             "Alquiler de equipo tecnológico")

            self.__equipo_id = equipo_id.upper().strip()
            self.__tipo_equipo = tipo_lower
            self.__incluye_seguro = incluye_seguro

            logger.info(f"AlquilerEquipo '{self.__equipo_id}' creado | "
                        f"Tipo: {self.__tipo_equipo} | "
                        f"Seguro: {incluye_seguro}")

        except ServicioError:
            raise
        except Exception as e:
            raise ServicioError(
                f"Error al crear AlquilerEquipo: {e}", "SFJ-300"
            ) from e

    @property
    def equipo_id(self) -> str:
        return self.__equipo_id

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def incluye_seguro(self) -> bool:
        return self.__incluye_seguro

    def calcular_costo(self, duracion_horas: float,
                       impuesto: float = None,
                       descuento: float = 0.0,
                       cliente_premium: bool = False) -> float:
        """
        POLIMORFISMO + SOBRECARGA: calcula el costo del alquiler.

        Lógica específica:
            - Factor de costo según tipo de equipo
            - Cargo de seguro del 5% si aplica
            - Descuento de volumen: >24h → -5% adicional
            - Cliente premium: -8% adicional

        Returns:
            float: Costo total del alquiler
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion_horas)

            # Tarifa ajustada según tipo de equipo
            factor = self.FACTOR_TIPO.get(self.__tipo_equipo, 1.0)
            tarifa_ajustada = self.tarifa_base * factor
            costo_base = tarifa_ajustada * duracion_horas

            # Cargo por seguro (5%)
            if self.__incluye_seguro:
                costo_base *= 1.05

            # Descuento de volumen para alquileres largos
            descuento_total = descuento
            if duracion_horas > 24:
                descuento_total += 0.05    # -5% por alquiler largo

            # Descuento cliente premium
            if cliente_premium:
                descuento_total += 0.08   # -8% adicional

            descuento_total = min(descuento_total, 0.50)
            costo_con_descuento = costo_base * (1 - descuento_total)

            tasa_impuesto = impuesto if impuesto is not None \
                else self.IVA_GENERAL
            if not isinstance(tasa_impuesto, (int, float)) \
                    or tasa_impuesto < 0:
                raise ParametroInvalidoError("impuesto",
                                             "debe ser un número no negativo")

            costo_final = costo_con_descuento * (1 + tasa_impuesto)

            if costo_final < 0:
                raise CostoInvalidoError(
                    f"resultado negativo: ${costo_final:.2f}"
                )

            detalle = (f"Equipo {self.__equipo_id} ({self.__tipo_equipo}) | "
                       f"{duracion_horas}h | Seguro={self.__incluye_seguro} | "
                       f"Desc={descuento_total*100:.0f}% | "
                       f"IVA={tasa_impuesto*100:.0f}%")
            self._registrar_calculo(costo_final, detalle)

            return round(costo_final, 2)

        except ServicioError:
            raise
        except Exception as e:
            raise CostoInvalidoError(str(e)) from e

        finally:
            logger.debug(f"[AlquilerEquipo-{self.__equipo_id}] "
                         f"Cálculo de costo procesado.")

    def describir(self) -> str:
        """
        POLIMORFISMO: descripción detallada del equipo en alquiler.
        """
        factor = self.FACTOR_TIPO.get(self.__tipo_equipo, 1.0)
        return (
            f"╔══ ALQUILER DE EQUIPO ═══════════════════════╗\n"
            f"  ID Equipo     : {self.__equipo_id}\n"
            f"  Tipo          : {self.__tipo_equipo.capitalize()}\n"
            f"  Tarifa base   : ${self.tarifa_base:.2f}/hora\n"
            f"  Factor tipo   : x{factor} (depreciación/riesgo)\n"
            f"  Seguro        : "
            f"{'Incluido (+5%)' if self.__incluye_seguro else 'No incluido'}\n"
            f"  Desc. volumen : -5% si > 24 horas\n"
            f"  Duración      : {self.DURACION_MINIMA}h – "
            f"{self.DURACION_MAXIMA}h\n"
            f"  Estado        : "
            f"{'✅ Disponible' if self.disponible else '❌ No disponible'}\n"
            f"╚═════════════════════════════════════════════╝"
        )

    def validar_parametros(self, duracion_horas: float,
                           **kwargs) -> bool:
        """
        POLIMORFISMO: validaciones específicas para alquiler de equipo.
        """
        try:
            if not isinstance(duracion_horas, (int, float)):
                raise ParametroInvalidoError("duracion_horas",
                                             "debe ser un número")
            if not (self.DURACION_MINIMA <= duracion_horas
                    <= self.DURACION_MAXIMA):
                raise DuracionInvalidaError(
                    self.DURACION_MINIMA,
                    self.DURACION_MAXIMA,
                    duracion_horas
                )

            logger.debug(f"[AlquilerEquipo-{self.__equipo_id}] "
                         f"Parámetros válidos: {duracion_horas}h")
            return True

        except ServicioError:
            raise
        except Exception as e:
            raise ParametroInvalidoError("validación", str(e)) from e


# =============================================================
# CLASE HIJA 3: AsesoriaEspecializada
# Servicio de asesorías técnicas o empresariales
# =============================================================

class AsesoriaEspecializada(Servicio):
    """
    HERENCIA de Servicio.
    Gestiona asesorías especializadas ofrecidas por Software FJ.

    Categorías: desarrollo, arquitectura, seguridad, datos, gestion
    Incluye tarifa diferencial según nivel del asesor y modalidad.

    POLIMORFISMO: lógica de costo, descripción y validación propias.
    """

    CATEGORIAS_VALIDAS = {
        "desarrollo", "arquitectura", "seguridad", "datos", "gestion"
    }
    MODALIDADES_VALIDAS = {"presencial", "virtual"}
    DURACION_MINIMA = 0.5     # Mínimo 30 minutos
    DURACION_MAXIMA = 4.0     # Máximo 4 horas por sesión

    # Factor de tarifa según nivel del asesor
    NIVEL_FACTOR = {
        "junior":   1.0,
        "senior":   1.5,
        "experto":  2.0
    }

    def __init__(self, asesoria_id: str, categoria: str,
                 tarifa_base: float, nivel_asesor: str = "senior",
                 modalidad: str = "virtual"):
        """
        Constructor de AsesoriaEspecializada.

        Args:
            asesoria_id (str): Identificador de la asesoría
            categoria (str): Área de la asesoría
            tarifa_base (float): Precio base por hora
            nivel_asesor (str): junior, senior o experto
            modalidad (str): presencial o virtual
        """
        try:
            cat = categoria.lower().strip() \
                if isinstance(categoria, str) else ""
            if cat not in self.CATEGORIAS_VALIDAS:
                raise ParametroInvalidoError(
                    "categoria",
                    f"debe ser una de: {', '.join(self.CATEGORIAS_VALIDAS)}"
                )

            nivel = nivel_asesor.lower().strip() \
                if isinstance(nivel_asesor, str) else ""
            if nivel not in self.NIVEL_FACTOR:
                raise ParametroInvalidoError(
                    "nivel_asesor",
                    f"debe ser: {', '.join(self.NIVEL_FACTOR.keys())}"
                )

            mod = modalidad.lower().strip() \
                if isinstance(modalidad, str) else ""
            if mod not in self.MODALIDADES_VALIDAS:
                raise ParametroInvalidoError(
                    "modalidad",
                    f"debe ser: {', '.join(self.MODALIDADES_VALIDAS)}"
                )

            nombre = f"Asesoría {cat.capitalize()} [{asesoria_id}]"
            super().__init__(nombre, tarifa_base,
                             f"Asesoría especializada en {cat}")

            self.__asesoria_id = asesoria_id.upper().strip()
            self.__categoria = cat
            self.__nivel_asesor = nivel
            self.__modalidad = mod
            self.__sesiones_realizadas = 0

            logger.info(f"AsesoriaEspecializada '{self.__asesoria_id}' "
                        f"creada | Cat: {cat} | Nivel: {nivel} | "
                        f"Modalidad: {mod}")

        except ServicioError:
            raise
        except Exception as e:
            raise ServicioError(
                f"Error al crear AsesoriaEspecializada: {e}", "SFJ-300"
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
            - Factor de tarifa según nivel del asesor
            - Modalidad presencial: +20% sobre tarifa
            - Cliente premium: descuento del 15%
            - Paquete multi-sesión: si sesiones > 5, -10%

        Returns:
            float: Costo total de la asesoría
        """
        try:
            self.verificar_disponibilidad()
            self.validar_parametros(duracion_horas)

            # Tarifa ajustada por nivel del asesor
            factor_nivel = self.NIVEL_FACTOR.get(self.__nivel_asesor, 1.0)
            tarifa_ajustada = self.tarifa_base * factor_nivel

            # Extra por modalidad presencial
            if self.__modalidad == "presencial":
                tarifa_ajustada *= 1.20   # +20%

            costo_base = tarifa_ajustada * duracion_horas

            # Descuentos acumulables
            descuento_total = descuento
            if cliente_premium:
                descuento_total += 0.15   # -15% premium

            # Descuento por fidelidad (más de 5 sesiones previas)
            if self.__sesiones_realizadas > 5:
                descuento_total += 0.10   # -10% fidelidad

            descuento_total = min(descuento_total, 0.50)
            costo_con_descuento = costo_base * (1 - descuento_total)

            tasa_impuesto = impuesto if impuesto is not None \
                else self.IVA_GENERAL
            if not isinstance(tasa_impuesto, (int, float)) \
                    or tasa_impuesto < 0:
                raise ParametroInvalidoError("impuesto",
                                             "debe ser un número no negativo")

            costo_final = costo_con_descuento * (1 + tasa_impuesto)

            if costo_final < 0:
                raise CostoInvalidoError(
                    f"resultado negativo: ${costo_final:.2f}"
                )

            detalle = (
                f"Asesoría {self.__asesoria_id} | {self.__categoria} | "
                f"Nivel={self.__nivel_asesor} | {self.__modalidad} | "
                f"{duracion_horas}h | Desc={descuento_total*100:.0f}% | "
                f"IVA={tasa_impuesto*100:.0f}%"
            )
            self._registrar_calculo(costo_final, detalle)

            # Contabiliza la sesión
            self.__sesiones_realizadas += 1

            return round(costo_final, 2)

        except ServicioError:
            raise
        except Exception as e:
            raise CostoInvalidoError(str(e)) from e

        finally:
            logger.debug(f"[AsesoriaEspecializada-{self.__asesoria_id}] "
                         f"Cálculo de costo procesado.")

    def describir(self) -> str:
        """
        POLIMORFISMO: descripción detallada de la asesoría.
        """
        factor = self.NIVEL_FACTOR.get(self.__nivel_asesor, 1.0)
        return (
            f"╔══ ASESORÍA ESPECIALIZADA ═══════════════════╗\n"
            f"  ID Asesoría   : {self.__asesoria_id}\n"
            f"  Categoría     : {self.__categoria.capitalize()}\n"
            f"  Nivel asesor  : {self.__nivel_asesor.capitalize()} "
            f"(x{factor} tarifa)\n"
            f"  Modalidad     : {self.__modalidad.capitalize()}"
            f"{'(+20%)' if self.__modalidad == 'presencial' else ''}\n"
            f"  Tarifa base   : ${self.tarifa_base:.2f}/hora\n"
            f"  Sesiones prev.: {self.__sesiones_realizadas}\n"
            f"  Desc. fidelid.: -10% si > 5 sesiones previas\n"
            f"  Duración      : {self.DURACION_MINIMA}h – "
            f"{self.DURACION_MAXIMA}h por sesión\n"
            f"  Estado        : "
            f"{'✅ Disponible' if self.disponible else '❌ No disponible'}\n"
            f"╚═════════════════════════════════════════════╝"
        )

    def validar_parametros(self, duracion_horas: float,
                           **kwargs) -> bool:
        """
        POLIMORFISMO: validaciones específicas para asesorías.
        """
        try:
            if not isinstance(duracion_horas, (int, float)):
                raise ParametroInvalidoError("duracion_horas",
                                             "debe ser un número")
            if not (self.DURACION_MINIMA <= duracion_horas
                    <= self.DURACION_MAXIMA):
                raise DuracionInvalidaError(
                    self.DURACION_MINIMA,
                    self.DURACION_MAXIMA,
                    duracion_horas
                )

            logger.debug(f"[AsesoriaEspecializada-{self.__asesoria_id}] "
                         f"Parámetros válidos: {duracion_horas}h")
            return True

        except ServicioError:
            raise
        except Exception as e:
            raise ParametroInvalidoError("validación", str(e)) from e


# =============================================================
# FUNCIÓN DE DEMOSTRACIÓN
# Simula operaciones válidas e inválidas para evidenciar el módulo
# =============================================================

def demostrar_modulo_servicios():
    """
    Demuestra el funcionamiento del módulo de servicios con operaciones
    válidas e inválidas, evidenciando herencia, polimorfismo, sobrecarga
    y manejo de excepciones.
    """
    print("\n" + "="*58)
    print("  SOFTWARE FJ — MÓDULO 3: SERVICIOS ESPECIALIZADOS")
    print("  Integrante: Hernán David Olaya Martínez")
    print("="*58)

    # ── Creación de servicios válidos ──────────────────────────────
    print("\n▶ 1. Creación de servicios especializados (herencia):")
    sala = ReservaSala("SALA-A1", capacidad_maxima=10,
                       tarifa_base=50.0, equipada=True)
    equipo = AlquilerEquipo("EQ-001", tipo_equipo="laptop",
                            tarifa_base=20.0, incluye_seguro=True)
    asesoria = AsesoriaEspecializada("ASE-001", categoria="seguridad",
                                     tarifa_base=80.0,
                                     nivel_asesor="experto",
                                     modalidad="presencial")
    print("  ✅ ReservaSala, AlquilerEquipo y AsesoriaEspecializada creados.")

    # ── Polimorfismo: describir() ──────────────────────────────────
    print("\n▶ 2. Polimorfismo — describir() (misma llamada, distinto resultado):")
    for servicio in [sala, equipo, asesoria]:
        print(servicio.describir())

    # ── Sobrecarga: calcular_costo() con distintos parámetros ─────
    print("\n▶ 3. Sobrecarga — calcular_costo() con distintas firmas:")

    # Modo 1: solo duración
    costo1 = sala.calcular_costo(3)
    print(f"  Sala (3h, sin extras)         : ${costo1:.2f}")

    # Modo 2: duración + impuesto personalizado
    costo2 = equipo.calcular_costo(10, impuesto=0.10)
    print(f"  Equipo (10h, IVA 10%)         : ${costo2:.2f}")

    # Modo 3: duración + descuento + cliente premium
    costo3 = asesoria.calcular_costo(2, descuento=0.05,
                                     cliente_premium=True)
    print(f"  Asesoría (2h, desc+premium)   : ${costo3:.2f}")

    # Modo 4: todos los parámetros
    costo4 = sala.calcular_costo(4, impuesto=0.19,
                                 descuento=0.10, cliente_premium=True)
    print(f"  Sala (4h, IVA+desc+premium)   : ${costo4:.2f}")

    # ── Manejo de excepciones: operaciones inválidas ───────────────
    print("\n▶ 4. Manejo de excepciones (operaciones inválidas):")

    # Servicio con tipo de equipo inválido
    print("\n  [a] Tipo de equipo inválido:")
    try:
        malo = AlquilerEquipo("EQ-BAD", tipo_equipo="avion",
                              tarifa_base=10.0)
    except ServicioError as e:
        print(f"      Capturado → {e}")

    # Duración fuera de rango
    print("\n  [b] Duración fuera de rango en ReservaSala:")
    try:
        sala.calcular_costo(12)   # máximo es 8h
    except DuracionInvalidaError as e:
        print(f"      Capturado → {e}")

    # Servicio desactivado
    print("\n  [c] Intentar usar servicio desactivado:")
    try:
        equipo.desactivar()
        equipo.calcular_costo(5)
    except ServicioNoDisponibleError as e:
        print(f"      Capturado → {e}")
    else:
        print("      No se lanzó excepción (inesperado).")
    finally:
        equipo.activar()    # Reactiva para uso posterior
        print("      (Servicio reactivado en bloque finally)")

    # Tarifa base inválida
    print("\n  [d] Tarifa base negativa (try/except/else):")
    try:
        sala.tarifa_base = -100
    except ServicioError as e:
        print(f"      Capturado → {e}")
    else:
        print("      Tarifa actualizada correctamente.")

    # ── Historial de costos ────────────────────────────────────────
    print("\n▶ 5. Historial de cálculos de costo (ReservaSala):")
    for i, entrada in enumerate(sala.obtener_historial_costos(), 1):
        print(f"  {i}. ${entrada['costo']:.2f} | {entrada['timestamp']}")

    print("\n✅ Módulo 3 completado. Logs guardados en logs/software_fj.log")
    print("="*58 + "\n")


# =============================================================
# PUNTO DE ENTRADA
# =============================================================
if __name__ == "__main__":
    demostrar_modulo_servicios()

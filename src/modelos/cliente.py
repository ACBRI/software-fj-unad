"""
Módulo: Gestión de Clientes con Validaciones Robustas

Desarrollado por: Jhon Alejandro Betancurt Osorio (issue #2, rama feat/cliente)
Integrado con el núcleo del sistema por: Andrés Camilo Briñez Núñez

Validaciones implementadas:
    - Cédula: solo dígitos, 7 a 10 caracteres.
    - Nombre: no vacío, mínimo 3 caracteres, sin números.
    - Email: regex r'^[\\w.+-]+@[\\w-]+\\.[\\w.-]+$'.
    - Teléfono: 7 a 15 dígitos, prefijo '+' opcional.
"""

import re

from src.core.entidad_base import EntidadBase
from src.core.excepciones import ClienteInvalidoError
from src.core.logger import obtener_logger

_log = obtener_logger(__name__)


class Cliente(EntidadBase):
    """Cliente del sistema Software FJ con validaciones estrictas en setters."""

    def __init__(self, cedula, nombre, email, telefono):
        super().__init__(identificador=str(cedula))
        self.cedula = cedula
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # --- Atributos encapsulados con @property y validación en setters ---

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, valor):
        if not str(valor).isdigit() or not (7 <= len(str(valor)) <= 10):
            msg = f"Cédula inválida: {valor}. Debe ser numérica (7-10 dígitos)."
            _log.error(msg)
            raise ClienteInvalidoError(msg)
        self._cedula = str(valor)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3 or any(c.isdigit() for c in valor):
            msg = "Nombre inválido: No debe estar vacío, tener mínimo 3 letras y no contener números."
            _log.error(msg)
            raise ClienteInvalidoError(msg)
        self._nombre = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        regex = r'^[\w.+-]+@[\w-]+\.[\w.-]+$'
        if not re.match(regex, str(valor)):
            msg = f"Email inválido: {valor}. No cumple con el formato estándar."
            _log.error(msg)
            raise ClienteInvalidoError(msg)
        self._email = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = str(valor).replace("+", "")
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            msg = f"Teléfono inválido: {valor}. Debe tener entre 7 y 15 dígitos."
            _log.error(msg)
            raise ClienteInvalidoError(msg)
        self._telefono = valor

    # --- Métodos abstractos heredados de EntidadBase ---

    def validar(self):
        """Confirma la integridad de los atributos (los setters ya validaron)."""
        return True

    def describir(self):
        """Descripción legible del cliente."""
        return f"Cliente: {self.nombre} | C.C: {self.cedula} | Email: {self.email} | Tel: {self.telefono}"

    def __str__(self):
        return self.describir()


# --- Bloque de pruebas manuales (preservado del autor original) ---
if __name__ == "__main__":
    print("--- Iniciando pruebas del módulo Cliente ---")
    try:
        c1 = Cliente("10123456", "Alejandro Betancurt", "jhabetancurt@unad.edu.co", "3115576583")
        print(f"ÉXITO: {c1.describir()}")

        print("\nProbando cédula inválida...")
        c2 = Cliente("123", "Jhon", "error@test.com", "3001234")
    except ClienteInvalidoError as e:
        print(f"CAPTURA CORRECTA: {e}")

    try:
        print("\nProbando email inválido...")
        c3 = Cliente("10203040", "Carlos Perez", "email_malo_sin_arroba", "3005554433")
    except ClienteInvalidoError as e:
        print(f"CAPTURA CORRECTA: {e}")

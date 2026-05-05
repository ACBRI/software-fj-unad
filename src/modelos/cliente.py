import re
import logging

# Configuración del registro de errores en archivo de logs
logging.basicConfig(
    filename='software_fj_errors.log', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Excepción personalizada exigida en el Issue #2
class ClienteInvalidoError(Exception):
    """Excepción lanzada cuando los datos del cliente no cumplen el contrato"""
    pass

class Cliente: 
    """
    Desarrollado por: Jhon Alejandro Betancurt Osorio
    Módulo: Gestión de Clientes con Validaciones Robustas
    """

    def __init__(self, cedula, nombre, email, telefono):
        # La asignación invoca automáticamente a los @setters para validar
        self.cedula = cedula
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # --- Atributos Encapsulados con @property ---

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, valor):
        # Validación: Solo dígitos, entre 7 y 10 caracteres
        if not str(valor).isdigit() or not (7 <= len(str(valor)) <= 10):
            msg = f"Cédula inválida: {valor}. Debe ser numérica (7-10 dígitos)."
            logging.error(msg)
            raise ClienteInvalidoError(msg)
        self._cedula = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # Validación: No vacío, mín 3 caracteres, sin números
        if not valor or len(valor.strip()) < 3 or any(char.isdigit() for char in valor):
            msg = "Nombre inválido: No debe estar vacío, tener mín 3 letras y no contener números."
            logging.error(msg)
            raise ClienteInvalidoError(msg)
        self._nombre = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        # Validación con Regex según el contrato exigido
        regex = r'^[\w.+-]+@[\w-]+\.[\w.-]+$'
        if not re.match(regex, str(valor)):
            msg = f"Email inválido: {valor}. No cumple con el formato estándar."
            logging.error(msg)
            raise ClienteInvalidoError(msg)
        self._email = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        # Validación: 7-15 dígitos
        limpio = str(valor).replace("+", "")
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            msg = f"Teléfono inválido: {valor}. Debe tener entre 7 y 15 dígitos."
            logging.error(msg)
            raise ClienteInvalidoError(msg)
        self._telefono = valor

    # --- Métodos Obligatorios a Sobrescribir ---

    def validar(self):
        """Verifica que todos los atributos sean correctos (exigido por EntidadBase)"""
        # Como los setters ya validan, este método confirma la integridad actual
        return True

    def describir(self):
        """Devuelve una descripción del cliente (exigido por EntidadBase)"""
        return f"Cliente: {self.nombre} | C.C: {self.cedula} | Email: {self.email} | Tel: {self.telefono}"

    def __str__(self):
        return self.describir()

# --- Bloque de Pruebas 
if __name__ == "__main__":
    print("--- Iniciando pruebas del módulo Cliente ---")
    try:
        # Prueba 1: Registro Válido
        c1 = Cliente("10123456", "Alejandro Betancurt", "jhabetancurt@unad.edu.co", "3115576583")
        print(f"ÉXITO: {c1.describir()}")

        # Prueba 2: Cédula corta (Inválida)
        print("\nProbando cédula inválida...")
        c2 = Cliente("123", "Jhon", "error@test.com", "3001234")
    except ClienteInvalidoError as e:
        print(f"CAPTURA CORRECTA: {e}")

    try:
        # Prueba 3: Email con formato incorrecto
        print("\nProbando email inválido...")
        c3 = Cliente("10203040", "Carlos Perez", "email_malo_sin_arroba", "3005554433")
    except ClienteInvalidoError as e:
        print(f"CAPTURA CORRECTA: {e}")
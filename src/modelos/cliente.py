"""
Clase Cliente — STUB pendiente de implementación.

Responsable: Jhon Alejandro Betancurt Osorio (issue #2)

Contrato mínimo esperado:
    - Atributos encapsulados: cedula, nombre, email, telefono
    - Validaciones estrictas en cada setter:
        * cedula: solo dígitos, 7-10 caracteres
        * email: formato usuario@dominio.tld
        * telefono: 7-15 dígitos, opcional prefijo +
        * nombre: no vacío, mínimo 3 caracteres
    - Debe lanzar ClienteInvalidoError ante datos inválidos
    - Hereda de EntidadBase y sobreescribe describir() + validar()
"""

from __future__ import annotations

from src.core.entidad_base import EntidadBase
from src.core.excepciones import ClienteInvalidoError


class Cliente(EntidadBase):
    """Placeholder — sustituir por la implementación de Jhon Alejandro."""

    def __init__(self, cedula: str, nombre: str, email: str, telefono: str) -> None:
        super().__init__(identificador=cedula)
        self._cedula = cedula
        self._nombre = nombre
        self._email = email
        self._telefono = telefono
        self.validar()

    @property
    def cedula(self) -> str:
        return self._cedula

    @property
    def nombre(self) -> str:
        return self._nombre

    def describir(self) -> str:
        return f"Cliente {self._nombre} (c.c. {self._cedula})"

    def validar(self) -> None:
        if not self._cedula or not self._cedula.isdigit():
            raise ClienteInvalidoError(
                f"Cédula inválida: {self._cedula!r} (debe contener solo dígitos)."
            )
        if not self._nombre or len(self._nombre.strip()) < 3:
            raise ClienteInvalidoError(
                f"Nombre inválido: {self._nombre!r} (mínimo 3 caracteres)."
            )
        if "@" not in self._email or "." not in self._email:
            raise ClienteInvalidoError(f"Email con formato inválido: {self._email!r}.")

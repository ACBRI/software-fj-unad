# Software FJ — Sistema Integral de Gestión de Clientes, Servicios y Reservas

> **Curso:** Programación (213023) · **Fase 4 — Componente práctico** · **Grupo 213023_378**
> **Universidad Nacional Abierta y a Distancia (UNAD)** — Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
> **Programa:** Ingeniería de Sistemas · **Periodo:** 15 abril – 12 mayo 2026

Aplicación Python orientada a objetos, sin base de datos, que gestiona clientes, servicios y reservas para la empresa ficticia **Software FJ**. Implementa de forma rigurosa los principios de abstracción, herencia, polimorfismo, encapsulación y manejo avanzado de excepciones, garantizando que el sistema siga funcionando aun cuando se presentan errores durante su ejecución.

---

## 📋 Tabla de contenido

- [Objetivo de aprendizaje](#-objetivo-de-aprendizaje)
- [Arquitectura](#-arquitectura)
- [Manejo de excepciones](#-manejo-de-excepciones)
- [Ejecución](#-ejecución)
- [Equipo y distribución de roles](#-equipo-y-distribución-de-roles)
- [Flujo de trabajo en Git](#-flujo-de-trabajo-en-git)
- [Criterios de evaluación cubiertos](#-criterios-de-evaluación-cubiertos)

---

## 🎯 Objetivo de aprendizaje

Implementar el manejo de excepciones en el desarrollo de aplicaciones orientadas a objetos buscando **estabilidad y robustez**, permitiendo una gestión adecuada de errores en el funcionamiento de las soluciones.

---

## 🏛️ Arquitectura

```
software-fj-unad/
├── main.py                           # Punto de entrada
├── src/
│   ├── core/                         # Núcleo del sistema
│   │   ├── entidad_base.py           # Clase abstracta raíz
│   │   ├── excepciones.py            # Jerarquía de excepciones personalizadas
│   │   └── logger.py                 # Logging centralizado (consola + archivo rotativo)
│   ├── modelos/
│   │   ├── cliente.py                # Cliente (validaciones + encapsulación)
│   │   ├── servicio.py               # Servicio (clase abstracta)
│   │   └── reserva.py                # Reserva (estados, confirmar, cancelar, procesar)
│   ├── servicios_especializados/
│   │   ├── reserva_sala.py           # Servicio concreto: reserva de sala
│   │   ├── alquiler_equipo.py        # Servicio concreto: alquiler de equipo
│   │   ├── asesoria_especializada.py # Servicio concreto: asesoría
│   │   └── gestor.py                 # Fachada orquestadora
│   └── simulaciones/
│       └── escenarios.py             # ≥10 operaciones válidas e inválidas
├── tests/
│   └── test_nucleo.py                # Pruebas unitarias
└── logs/
    └── sistema.log                   # Generado en runtime
```

### Principios POO aplicados

| Principio | Dónde se evidencia |
|-----------|--------------------|
| **Abstracción** | `EntidadBase` y `Servicio` son `ABC` con métodos abstractos |
| **Herencia** | `Cliente`, `Servicio`, `Reserva` → `EntidadBase` / `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` → `Servicio` |
| **Polimorfismo** | `describir()` y `calcular_costo()` sobreescritos por cada servicio |
| **Encapsulación** | Atributos `_privados` expuestos solo mediante `@property` |
| **Sobrecarga** | `Servicio.calcular_costo(horas, *, impuesto, descuento)` admite parámetros opcionales |

---

## 🛡️ Manejo de excepciones

### Jerarquía personalizada (`src/core/excepciones.py`)

```
SoftwareFJError (raíz)               → SFJ-000
├── DatosInvalidosError              → SFJ-100
│   └── ClienteInvalidoError         → SFJ-110
├── ServicioNoDisponibleError        → SFJ-200
├── ReservaInvalidaError             → SFJ-300
├── CalculoInconsistenteError        → SFJ-400
└── OperacionNoPermitidaError        → SFJ-500
```

### Patrones utilizados

- **`try / except / else / finally`** — presente en cada método de `GestorSistema`.
- **Encadenamiento** (`raise ... from ...`) — al envolver errores de bajo nivel.
- **Excepciones personalizadas** — una por dominio de fallo, con código trazable.
- **Aislamiento de escenarios** — cada simulación corre en un `try/except` propio; una falla no detiene las demás.
- **Logging automático** — toda excepción deja rastro en `logs/sistema.log` con nivel, módulo y código.

---

## 🚀 Ejecución

### Requisitos

- Python **≥ 3.10** (sin dependencias externas, solo biblioteca estándar)

### Correr la batería completa de simulaciones

```bash
python3 main.py
```

Se imprimen los 12 escenarios por consola y se vuelca el log completo en `logs/sistema.log`.

### Correr los tests unitarios

```bash
python3 -m unittest discover -s tests -v
```

---

## 👥 Equipo y distribución de roles

**Grupo 213023_378** — Tutor: Juan Pablo Zambrano Sanjuan

| # | Integrante | Rol | Módulo | Rama |
|---|------------|-----|--------|------|
| 1 | **Andrés Camilo Briñez Núñez** | Líder técnico | `src/core/*`, `gestor.py`, `main.py`, documentación | `feat/nucleo` |
| 2 | Jhon Alejandro Betancurt Osorio | Modelo cliente | `src/modelos/cliente.py` | `feat/cliente` |
| 3 | Hernán David Olaya Martínez | Jerarquía de servicios | `src/modelos/servicio.py`, `src/servicios_especializados/*` | `feat/servicios` |
| 4 | Wilmer García Ochoa | Modelo reserva + sobrecarga | `src/modelos/reserva.py` | `feat/reservas` |
| 5 | John Alexander Gaitán Barrera | Escenarios de simulación | `src/simulaciones/escenarios.py` | `feat/simulaciones` |

Cada integrante tiene una rama propia y un *issue* asignado en GitHub con el alcance detallado.

---

## 🔀 Flujo de trabajo en Git

1. **Clonar** el repositorio: `git clone <url>`
2. **Crear/ubicarse** en tu rama: `git checkout -b feat/<tu-modulo>`
3. **Implementar** el módulo que te corresponde (ver los stubs en el repo: cada uno tiene docstring con el contrato).
4. **Commitear** con mensajes descriptivos en imperativo (`feat:`, `fix:`, `docs:`, `test:`).
5. **Push** a tu rama: `git push origin feat/<tu-modulo>`
6. **Pull Request** hacia `main` cuando esté listo — asignar revisor y cerrar el issue correspondiente.
7. **Revisión cruzada** obligatoria: otro integrante aprueba antes del merge.

---

## 📊 Criterios de evaluación cubiertos

| Criterio (rúbrica) | Pts | Evidencia en el repo |
|--------------------|-----|----------------------|
| Manejo de excepciones (personalizadas, try/except/else/finally, encadenamiento, logs) | 50 | `src/core/excepciones.py`, `src/servicios_especializados/gestor.py`, `logs/sistema.log` |
| ≥10 simulaciones válidas e inválidas con logs | 35 | `src/simulaciones/escenarios.py` (12 escenarios), `logs/sistema.log` |
| Claridad y pertinencia del código | 35 | Arquitectura modular, tipos estáticos, docstrings en cada módulo |
| Trabajo colaborativo + uso profesional de GitHub | 30 | Ramas por integrante, PRs, issues asignados, este README |

**Total objetivo: 150 / 150 pts**

---

## 📚 Referencias

- Van Rossum, G., & Drake Jr, F. L. (2024). *El tutorial de Python*. Python Software Foundation. https://docs.python.org/es/3.12/tutorial/errors.html
- Cuevas Álvarez, A. (2016). *Python 3: curso práctico*. RA-MA Editorial.
- Zambrano, J. P. (2025). *Introducción al uso de GitHub*. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75876

# CRM Multitenant Backend (Python & MySQL)

Este proyecto es una refactorización sólida y segura de un sistema de gestión de clientes.

## Características Principales

- **Arquitectura Modular**: Separación en Modelos, Repositorios y Servicios (SOLID).
- **Seguridad**: Carga de credenciales mediante `.env` y hashing de contraseñas con `bcrypt`.
- **Integridad**: Manejo de transacciones atómicas y validación de reglas XOR para contactos.
- **Documentación**: Manual técnico detallado incluido.

## Requisitos

- Python 3.9+
- MySQL 8.0+
- `pip install -r requirements.txt`

## Instalación y Configuración

1. Clone el repositorio o copie los archivos.
2. Configure el archivo `.env` con sus credenciales (use `.env.example` como base).
3. **Migración de Seguridad**: Ejecute `migracion_login.sql` en su base de datos para habilitar el sistema de login.
4. Instale las dependencias: `pip install -r requirements.txt`.

## Ejecución

- **Demo rápida**: `python main.py`
- **Tests funcionales**: `python test_crm.py`
- **Documentación completa**: Consulte `MANUAL_PROYECTO.md`.

# 🏗️ CRM Industrial SaaS (Clean Architecture)

Este es un entorno CRM modular diseñado para escalabilidad industrial, utilizando un modelo SaaS con Multitenancy y una arquitectura agnóstica a la base de datos.

## 📖 Documentación Centralizada

Para comprender la arquitectura, configuración y flujos del sistema, consulte nuestro Manual Maestro:

👉 **[MANUAL_MAESTRO_CRM.md](docs/MANUAL_MAESTRO_CRM.md)** (Arquitectura, Seguridad, Flujos y Backup)

### Contenidos Clave en el Manual Maestro:

- **Clean Architecture**: Capas y principios de diseño.
- **Multitenancy**: Cómo funciona el aprovisionamiento de instancias privadas.
- **Configuración .env**: Variables necesarias para el despliegue.
- **Mantenimiento Masivo**: Uso del sistema de Broadcast.
- **Diccionario de Errores**: Mapeo técnico para el Frontend.

---

## 🛠️ Stack Tecnológico

Para ejecutar el proyecto en otro entorno, las librerías requeridas se encuentran listadas en el archivo `backend/requirements.txt`. (Esta es la ubicación estándar de la industria, en la raíz del entorno backend).

**Para instalar todas las dependencias, ejecute desde la raíz del proyecto:**
```bash
pip install -r backend/requirements.txt
```

Consulte el listado detallado de dependencias y versiones en:
👉 **[DEPENDENCIAS.md](docs/DEPENDENCIES.md)**

---

## 🔐 Seguridad e Integridad

El sistema implementa:

- **Autenticación Dual**: Persona Natural / Empresa con validación de RUT.
- **Higiene de Datos**: Deduplicación y normalización automática de contactos.
- **Aislamiento de Datos**: Cada tenant opera en su propia base de datos física.

---

_Proyecto desarrollado bajo estándares de alta disponibilidad y código limpio._

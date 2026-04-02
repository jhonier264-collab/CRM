# 🛠️ Dependencias Técnicas: CRM Industrial

Este documento detalla los requisitos y librerías necesarias para el funcionamiento y desarrollo del ecosistema CRM.

## 🐍 1. Backend (Python 3.10+)

Las librerías están gestionadas en `backend/requirements.txt`.

| Librería                 | Propósito         | Por qué se usa                                                 |
| :----------------------- | :---------------- | :------------------------------------------------------------- |
| `mysql-connector-python` | Driver MySQL      | Conexión robusta y nativa con el motor de base de datos.       |
| `pandas`                 | Análisis de Datos | Manejo eficiente de importación/exportación masiva y limpieza. |
| `python-dotenv`          | Configuración     | Gestión segura de credenciales mediante archivos `.env`.       |
| `bcrypt`                 | Seguridad         | Hashing de contraseñas de estándar industrial.                 |
| `PyJWT`                  | Autenticación     | Generación y validación de tokens de sesión seguros.           |

---

## ⚛️ 2. Frontend (Vite + Vanilla JS/React)

El frontend está optimizado para velocidad y modularidad.

- **Vite**: Motor de construcción ultrarrápido.
- **Axios**: Cliente HTTP para comunicación asíncrona con el Backend.
- **Lucide-React**: Iconografía profesional y consistente.

---

## 🛠️ 3. Herramientas de Desarrollo

Para mantener la calidad del código, se recomienda el uso de:

- **Git**: Control de versiones.
- **ESLint / Prettier**: Estándares de estilo.
- **Mermaid**: Generación automática de diagramas desde Markdown.

---

_Nota: Para instalar todas las dependencias del backend, ejecute `pip install -r backend/requirements.txt` dentro de un entorno virtual._

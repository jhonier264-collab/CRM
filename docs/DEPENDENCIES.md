# Requisitos del Proyecto CRM Industrial

Para configurar este proyecto en una nueva máquina, asegúrese de tener instalado lo siguiente:

## 1. Stack Tecnológico

- **Python 3.10+**: Lenguaje principal del backend.
- **MySQL 8.0+**: Motor de base de datos.
- **Node.js 18+**: Entorno de ejecución para React/Vite.
- **npm o yarn**: Gestor de paquetes.

## 2. Dependencias del Backend (Python)

Instalar mediante: `pip install -r backend/requirements.txt`

- `fastapi`: Framework API.
- `uvicorn`: Servidor ASGI.
- `mysql-connector-python`: Driver de base de datos.
- `pandas`: Procesamiento de datos (CSV).
- `bcrypt`: Seguridad de contraseñas.
- `python-multipart`: Soporte para carga de archivos.

## 3. Dependencias del Frontend (React)

Instalar mediante: `npm install` dentro de la carpeta `frontend`.

- `react`, `react-dom`: Núcleo de la interfaz.
- `lucide-react`: Set de iconos premium.
- `axios`: Cliente HTTP.
- `vite`: Herramienta de construcción y dev server.

## 4. Extensiones Recomendadas de VS Code

Para una mejor experiencia de desarrollo, busque e instale estas extensiones:

1. **ESLint**: Para calidad de código Javascript.
2. **Prettier - Code formatter**: Para formateo automático.
3. **Python (Microsoft)**: Soporte completo para Python.
4. **MySQL (Jun Han)**: Para explorar la DB directamente desde el editor.
5. **Tailwind CSS IntelliSense**: (Si se usa Tailwind en componentes futuros).
6. **Thunder Client**: Para probar los endpoints de la API (Alternativa a Postman).

## 5. Configuración de Base de Datos

- Crear base de datos `crm_industrial`.
- Ejecutar scripts en `database/scripts/`.
- Configurar credenciales en el archivo `.env` del backend.

# Manual Técnico y Operativo: CRM Industrial Full-Stack

## 1. Arquitectura del Proyecto (Root)

El proyecto está organizado en una estructura monorepo que separa claramente las responsabilidades:

- **`backend/`**: Núcleo de la aplicación en Python.
  - `src/`: Lógica, modelos y repositorios internacionalizados.
  - `tests/`: Suite de pruebas (ej. `test_update_audit.py`).
  - `.env`: Configuración segura de la base de datos.
- **`frontend/`**: Interfaz de usuario dinámica.
  - `index.html`: Punto de entrada de la web.
  - `css/`, `js/`, `assets/`: Recursos estáticos.
- **`database/`**: Gestión de persistencia.
  - `dumps/`: Copias de seguridad de la base de datos (CRM_English.sql).
  - `scripts/`: Scripts de migración y optimización.
- **`docs/`**: Documentación técnica y manuales.

---

## 2. Funcionalidades del Backend

### Operaciones CRUD y Auditoría

- **Actualización Parcial**: Métodos `update_*` que permiten modificar campos específicos sin riesgo.
- **Auditoría Automática**: Registro automático de `created_at` y `updated_at` en todas las tablas de contacto y entidades.
- **Eliminación Atómica**: Borrado en cascada para mantener la base de datos limpia.

### Seguridad

- **Bcrypt**: Hashing de contraseñas de alta seguridad.
- **Environment Driven**: Configuración cargada dinámicamente desde `backend/.env`.
- **Git Protection**: Archivos `.gitignore` en la raíz y en backend para proteger credenciales.

---

## 3. Instalación en un Nuevo PC

Si decide mover el proyecto o clonarlo desde un repositorio, siga estos pasos para que funcione correctamente:

1.  **Requisitos**: Tener instalado Python 3.8+ y MySQL Server.
2.  **Preparar Backend**:
    ```bash
    cd backend
    python -m venv venv                # Crear entorno virtual
    .\venv\Scripts\activate           # Activar (Windows)
    pip install -r requirements.txt   # Instalar dependencias
    ```
3.  **Configurar Variables**:
    - Copie el archivo `.env.example` y renómbrelo como `.env`.
    - Edite el `.env` con las credenciales de su MySQL local.
4.  **Restaurar Base de Datos**:
    - Importe el archivo `database/dumps/CRM_English.sql` en su servidor MySQL.

## 4. Manual de Operación

### Ejecución del Backend

Para correr el backend o sus pruebas, primero sitúese en la carpeta correspondiente:

```bash
cd backend
python main.py
python tests/test_update_audit.py
```

### Visualización del Frontend

Puede abrir directamente el archivo `frontend/index.html` en cualquier navegador moderno para comenzar a trabajar en la interfaz.

---

> [!IMPORTANT]
> Nunca comparta o suba el archivo `backend/.env` a repositorios públicos. El archivo `.gitignore` raíz está configurado para protegerlo.

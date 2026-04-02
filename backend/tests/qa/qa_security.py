import os
import sys
import logging
from dotenv import load_dotenv

# Add backend to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Load .env from root
load_dotenv(os.path.join(backend_dir, '..', '.env'))

# flake8: noqa: E402
from src.core.mysql_repository import MySQLRepository  # noqa: E402
from src.repositories.auth_repository import AuthRepository  # noqa: E402
from src.lib.shared_auth.services import AuthCore  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QA_SECURITY")


def test_lockout():
    # load_dotenv is now called at the top level
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('MASTER_DB_NAME'),
        'port': int(os.getenv('DB_PORT'))
    }
    db = MySQLRepository(config)
    auth_repo = AuthRepository(db)
    auth_service = AuthCore(auth_repo)

    username = "alpha_corp"  # Usuario creado en el test anterior
    logger.info(f"Probando bloqueo de cuenta para {username}...")

    # 1. Intentar loguear con clave errónea hasta bloquear
    for i in range(1, 7):  # Max attempts = 5
        res = auth_service.authenticate(username, "ClaveErronea123!")
        logger.info(f"Intento {i}: {res.get('error')}")

    # 2. Verificar que el último intento indica bloqueo
    final_res = auth_service.authenticate(username, "ClaveErronea123!")
    if "bloqueada" in final_res.get('error', '').lower():
        logger.info("BLOQUEO DE CUENTA CONFIRMADO.")
    else:
        logger.error("FALLO: La cuenta no se bloqueó tras 5 intentos.")

    # 3. Verificar independencia: Otro usuario debe poder loguear (si existe)
    # Por simplicidad, verificamos que no hay registros de bloqueo en beta_inc
    beta_user = auth_repo.get_user_by_identifier("beta_inc")
    if beta_user and (beta_user['failed_attempts'] == 0):
        logger.info("INDEP CONFIRMADA: Otros usuarios permanecen intactos.")
    else:
        logger.warning(
            "Beta_inc no encontrado o con intentos previos, "
            "pero los bloqueos son por ID."
        )


if __name__ == "__main__":
    test_lockout()

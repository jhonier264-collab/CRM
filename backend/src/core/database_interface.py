"""
Encabezado Profesional: Interfaz de Persistencia de Datos
Propósito: Definir un contrato genérico para el almacenamiento de datos, permitiendo que el 
núcleo del sistema sea agnóstico a la tecnología de base de datos (SQL, NoSQL, etc.).
Por qué: Seguir el principio de inversión de dependencia de Clean Architecture.
"""

from abc import ABC, abstractmethod #libreria para crear una clase de base abstracta
from typing import Any, Optional #libreria para tipado

class IDatabase(ABC):
    """
    Interfaz pura para el gestor de persistencia.
    Define los métodos esenciales sin acoplarse a tecnologías específicas (MySQL, PostgreSQL, etc.).
    """

    @abstractmethod
    def connect(self) -> Any:
        """Establece la conexión con el motor de persistencia."""
        pass

    @abstractmethod
    def execute_command(self, command: str, parameters: Optional[tuple] = None, perform_commit: bool = False, fetch_results: bool = True) -> Any:
        """
        Ejecuta una instrucción de datos (Command).
        - command: La instrucción a ejecutar.
        - parameters: Datos opcionales para la instrucción.
        - perform_commit: Si debe confirmar los cambios inmediatamente.
        - fetch_results: Si debe retornar los resultados de la operación.
        """
        pass

    @abstractmethod
    def start_transaction(self) -> Any:
        """Inicia un contexto de transacción para operaciones atómicas."""
        pass

    @abstractmethod
    def switch_database(self, database_name: str):
        """Cambia dinámicamente el esquema de base de datos actual."""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Libera los recursos y cierra cualquier conexión activa."""
        pass

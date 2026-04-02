from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

class ApiResponse:
    """
    Clase utilitaria para estandarizar las respuestas JSON de la API.
    Asegura que el cliente reciba siempre una estructura predecible.
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "Operación exitosa", status_code: int = 200) -> JSONResponse:
        """
        Retorna una respuesta de éxito con código 200 por defecto.
        """
        content = {
            "status": "success",
            "data": data,
            "message": message
        }
        return JSONResponse(status_code=status_code, content=jsonable_encoder(content))

    @staticmethod
    def error(message: str = "Ha ocurrido un error", data: Any = None, status_code: int = 400) -> JSONResponse:
        """
        Retorna una respuesta de error con código 400 por defecto.
        """
        content = {
            "status": "error",
            "data": data,
            "message": message
        }
        return JSONResponse(status_code=status_code, content=jsonable_encoder(content))

    @staticmethod
    def unauthorized(message: str = "No autorizado") -> JSONResponse:
        """
        Retorna una respuesta de error 401 (No autorizado).
        """
        return ApiResponse.error(message=message, status_code=401)

    @staticmethod
    def not_found(message: str = "Recurso no encontrado") -> JSONResponse:
        """
        Retorna una respuesta de error 404 (No encontrado).
        """
        return ApiResponse.error(message=message, status_code=404)

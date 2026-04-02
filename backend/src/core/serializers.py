import json
import logging
from typing import Any, Dict, List, Type, Union
from src.models.models import User, Company, Address, Phone, Email

# Configuración del logger para rastrear errores de serialización
logger = logging.getLogger(__name__)

class BaseSerializer:
    """
    Clase base para todos los serializadores.
    Proporciona métodos para convertir objetos a diccionarios y viceversa.
    """
    
    @staticmethod
    def to_json(obj: Any) -> Dict[str, Any]:
        """
        Convierte un objeto (modelo) a un diccionario JSON limpio.
        Elimina atributos internos que empiecen con '_'.
        """
        # Si el objeto ya es un diccionario, lo devolvemos filtrando claves internas
        if isinstance(obj, dict):
            return {k: v for k, v in obj.items() if not k.startswith('_')}
        
        # Si el objeto tiene el método __dict__, lo usamos para la conversión
        if hasattr(obj, "__dict__"):
            data = obj.__dict__.copy()
            # Filtramos atributos privados o protegidos de Python
            return {k: v for k, v in data.items() if not k.startswith('_')}
        
        # Si no se puede serializar, devolvemos una representación de cadena
        return str(obj)

class UserSerializer(BaseSerializer):
    """
    Serializador específico para la entidad Usuario.
    Asegura que los datos del usuario se entreguen en un formato JSON estándar.
    """
    @staticmethod
    def serialize(user: User) -> Dict[str, Any]:
        data = BaseSerializer.to_json(user)
        # Aquí se podrían añadir campos calculados o formatear fechas si fuera necesario
        return data

class CompanySerializer(BaseSerializer):
    """
    Serializador específico para la entidad Empresa.
    Filtra y organiza los datos de la empresa para la API.
    """
    @staticmethod
    def serialize(company: Company) -> Dict[str, Any]:
        return BaseSerializer.to_json(company)

class AddressSerializer(BaseSerializer):
    """
    Serializador para Direcciones.
    """
    @staticmethod
    def serialize(address: Address) -> Dict[str, Any]:
        return BaseSerializer.to_json(address)

class PhoneSerializer(BaseSerializer):
    """
    Serializador para Teléfonos.
    """
    @staticmethod
    def serialize(phone: Phone) -> Dict[str, Any]:
        return BaseSerializer.to_json(phone)

class EmailSerializer(BaseSerializer):
    """
    Serializador para Correos Electrónicos.
    """
    @staticmethod
    def serialize(email: Email) -> Dict[str, Any]:
        return BaseSerializer.to_json(email)

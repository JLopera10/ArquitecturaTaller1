from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ProductDTO(BaseModel):
    """
    Objeto de transferencia de datos (DTO) para productos.

    Utiliza Pydantic para validar automáticamente los tipos de datos y asegurar
    que los atributos cumplen las restricciones de negocio, como valores positivos
    y stock válido.

    Attributes:
        id (Optional[int]): Identificador único del producto.
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría a la que pertenece el producto.
        size (str): Talla o dimensión principal.
        color (str): Color principal del producto.
        price (float): Precio del producto, debe ser mayor a 0.
        stock (int): Unidades disponibles, no puede ser negativo.
        description (str): Texto descriptivo del producto.
    """

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    model_config = {
        "from_attributes": True
    }

    @field_validator('price')
    def price_must_be_positive(cls, v):
        """
        Valida que el precio del producto sea mayor a 0.

        Args:
            v (float): Valor del precio a validar.

        Returns:
            float: Valor del precio si es válido.

        Raises:
            ValueError: Si el precio es menor o igual a 0.

        Example:
            >>> ProductDTO(price=120.0, ...)
            # correcto
            >>> ProductDTO(price=0, ...)
            # ValueError: El precio debe ser mayor a 0
        """
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator('stock')
    def stock_must_be_non_negative(cls, v):
        """
        Valida que el stock del producto no sea negativo.

        Args:
            v (int): Stock a validar.

        Returns:
            int: Valor del stock si es válido.

        Raises:
            ValueError: Si el stock es negativo.

        Example:
            >>> ProductDTO(stock=5, ...)
            # correcto
            >>> ProductDTO(stock=-1, ...)
            # ValueError: El stock no puede ser negativo
        """
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v

class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes enviados por el usuario al chat.

    Este modelo valida que el mensaje y el session_id no estén vacíos,
    facilitando la gestión de sesiones de conversación en la aplicación.

    Attributes:
        session_id (str): Identificador único de la sesión del usuario.
        message (str): Texto enviado por el usuario.
    """

    session_id: str
    message: str

    @field_validator('message')
    def message_not_empty(cls, v):
        """
        Valida que el mensaje no esté vacío o solo espacios.

        Args:
            v (str): Mensaje recibido.

        Returns:
            str: Mensaje si es válido.

        Raises:
            ValueError: Si el mensaje está vacío.

        Example:
            >>> ChatMessageRequestDTO(session_id="xyz", message="Hola")
            # correcto
            >>> ChatMessageRequestDTO(session_id="xyz", message="")
            # ValueError: El mensaje no puede estar vacío
        """
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v

    @field_validator('session_id')
    def session_id_not_empty(cls, v):
        """
        Valida que el session_id no esté vacío o solo espacios.

        Args:
            v (str): Identificador de sesión recibido.

        Returns:
            str: session_id si es válido.

        Raises:
            ValueError: Si el session_id está vacío.

        Example:
            >>> ChatMessageRequestDTO(session_id="abc", message="Hola")
            # correcto
            >>> ChatMessageRequestDTO(session_id="   ", message="Hola")
            # ValueError: El session_id no puede estar vacío
        """
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío")
        return v

class ChatMessageResponseDTO(BaseModel):
    """
    DTO para enviar respuestas del asistente de chat hacia el usuario.

    Este objeto incluye toda la información relevante para la respuesta,
    incluyendo los mensajes involucrados y el timestamp de la interacción.

    Attributes:
        session_id (str): Identificador de la sesión de chat.
        user_message (str): Mensaje enviado por el usuario.
        assistant_message (str): Respuesta generada por la IA.
        timestamp (datetime): Momento en que se generó la respuesta.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime

class ChatHistoryDTO(BaseModel):
    """
    DTO para mostrar mensajes previos en el historial de chat.

    Usado para listar mensajes anteriores de una sesión, mostrando
    la secuencia de turnos en la conversación.

    Attributes:
        id (int): Identificador único del mensaje en el historial.
        role (str): Rol que envió el mensaje ('user' o 'assistant').
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora del mensaje.
    """

    id: int
    role: str
    message: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }

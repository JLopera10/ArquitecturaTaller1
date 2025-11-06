"""
Excepciones específicas del dominio.

Estas clases representan errores de negocio controlados, distintos a errores técnicos,
y facilitan un manejo más claro y semántico de las fallas durante el flujo de la aplicación.
"""

class ProductNotFoundError(Exception):
    """
    Excepción lanzada cuando se intenta acceder a un producto inexistente.

    Esta excepción indica que la entidad producto solicitada por ID no ha sido localizada
    en el repositorio o sistema.

    Attributes:
        message (str): Mensaje descriptivo del error.

    Example:
        >>> raise ProductNotFoundError(7)
    """

    def __init__(self, product_id: int = None):
        """
        Inicializa la excepción opcionalmente con el ID del producto faltante.

        Args:
            product_id (int, optional): ID del producto que no se encontró.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado"
        else:
            self.message = "Producto no encontrado"
        super().__init__(self.message)

class InvalidProductDataError(Exception):
    """
    Excepción lanzada ante datos inválidos para la creación o actualización de productos.

    Se utiliza para reportar violaciones a reglas de negocio durante la validación
    de un producto.

    Attributes:
        message (str): Mensaje descriptivo del error.

    Example:
        >>> raise InvalidProductDataError("El precio debe ser positivo")
    """

    def __init__(self, message: str = None):
        """
        Inicializa la excepción detallando el motivo de invalidez.

        Args:
            message (str, optional): Mensaje específico de error de validación.
        """
        if message:
            self.message = f"Datos de producto inválidos: {message}"
        else:
            self.message = "Datos de producto inválidos"
        super().__init__(self.message)

class ChatServiceError(Exception):
    """
    Excepción lanzada ante errores en el procesamiento del servicio de chat.

    Usada para encapsular errores relacionados al flujo conversacional,
    externos al dominio puro, como llamadas a IA o errores de infraestructura.

    Attributes:
        message (str): Mensaje descriptivo del error.

    Example:
        >>> raise ChatServiceError("Fallo al generar respuesta IA")
    """

    def __init__(self, message: str = None):
        """
        Inicializa la excepción con un mensaje explicativo del problema.

        Args:
            message (str, optional): Detalle del error.
        """
        if message:
            self.message = f"Error en el servicio de chat: {message}"
        else:
            self.message = "Error en el servicio de chat"
        super().__init__(self.message)

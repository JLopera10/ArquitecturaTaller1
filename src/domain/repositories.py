from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage

class IProductRepository(ABC):
    """
    Interfaz abstracta para el acceso y manejo de productos en el repositorio.

    Define el contrato que las implementaciones concretas (bases de datos, mocks, etc.)
    deben cumplir para operar sobre productos dentro del sistema.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene la lista completa de productos registrados.

        Returns:
            List[Product]: Lista, posiblemente vacía, con todos los productos existentes.

        Example:
            >>> productos = repo.get_all()
        """
        raise NotImplementedError()

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto según su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: El producto si se encontró, o None en caso contrario.

        Example:
            >>> repo.get_by_id(10)
        """
        raise NotImplementedError()

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene productos filtrados por marca.

        Args:
            brand (str): Nombre de la marca (la comparación puede ser case-insensitive).

        Returns:
            List[Product]: Lista de productos que corresponden a la marca.

        Example:
            >>> repo.get_by_brand("Nike")
        """
        raise NotImplementedError()

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene productos filtrados por categoría.

        Args:
            category (str): Nombre de la categoría.

        Returns:
            List[Product]: Lista de productos que corresponden a la categoría.

        Example:
            >>> repo.get_by_category("deporte")
        """
        raise NotImplementedError()

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en el repositorio.

        Comportamiento esperado:
            - Si product.id es None: crea un nuevo producto y asigna ID.
            - Si product.id existe: actualiza el producto correspondiente.

        Args:
            product (Product): Instancia de Product a guardar.

        Returns:
            Product: Producto guardado (incluyendo el ID si fue recién creado).

        Example:
            >>> repo.save(Product(id=None, ...))  # crea nuevo
            >>> repo.save(Product(id=5, ...))    # actualiza
        """
        raise NotImplementedError()

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto específico por su identificador único.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto existía y fue eliminado, False si no existía.

        Example:
            >>> repo.delete(2)
        """
        raise NotImplementedError()

class IChatRepository(ABC):
    """
    Interfaz abstracta para el manejo del historial de conversaciones de chat.

    Permite definir repositorios concretos para almacenar, consultar y gestionar
    mensajes en múltiples sesiones.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje en el historial asociado a su sesión.

        Args:
            message (ChatMessage): Mensaje a almacenar. Si la implementación gestiona IDs,
                                   debe asignar uno.

        Returns:
            ChatMessage: Mensaje guardado, potencialmente con ID asignado.

        Example:
            >>> repo.save_message(msg)
        """
        raise NotImplementedError()

    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Recupera el historial completo de mensajes de una sesión (ordenados por antigüedad).

        Args:
            session_id (str): Identificador único de la sesión de chat.
            limit (Optional[int], optional): Si se especifica, retorna solo los últimos N mensajes.

        Returns:
            List[ChatMessage]: Lista de mensajes, ordenados por timestamp (más antiguos primero).

        Example:
            >>> repo.get_session_history("session-abc", limit=5)
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina el historial completo de una sesión de chat.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.

        Example:
            >>> repo.delete_session_history("session-abc")
        """
        raise NotImplementedError()

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Recupera los últimos N mensajes de una sesión, ordenados cronológicamente.

        Args:
            session_id (str): Identificador único de la sesión.
            count (int): Cantidad de mensajes a retornar (los N más recientes).

        Returns:
            List[ChatMessage]: Lista de mensajes recientes, de más viejo a más nuevo.

        Example:
            >>> repo.get_recent_messages("session-xyz", count=3)
        """
        raise NotImplementedError()

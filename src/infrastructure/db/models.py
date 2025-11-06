from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from datetime import datetime
from src.infrastructure.db.database import Base

class ProductModel(Base):
    """
    Modelo ORM que representa los productos de la tienda de e-commerce.

    La clase mapea la tabla 'products' en la base de datos, permitiendo
    persistir y consultar información relacionada con productos.

    Attributes:
        id (int): Identificador único del producto (clave primaria, autoincremental).
        name (str): Nombre del producto, no nulo e indexado.
        brand (str): Marca del producto, indexada.
        category (str): Categoría del producto, indexada.
        size (str): Talla o dimensión principal del producto.
        color (str): Color principal.
        price (float): Precio del producto.
        stock (int): Cantidad disponible.
        description (str): Descripción textual del producto.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    brand = Column(String(100), index=True)
    category = Column(String(100), index=True)
    size = Column(String(20))
    color = Column(String(50))
    price = Column(Float)
    stock = Column(Integer)
    description = Column(Text)

    def __repr__(self):
        """
        Representación legible y útil de la entidad de producto para debugging.

        Returns:
            str: Cadena representativa del producto.
        
        Example:
            >>> print(ProductModel(id=1, name="Nike", ...))
            <ProductModel(id=1, name='Nike', brand='Nike', price=120.0, stock=8)>
        """
        return f"<ProductModel(id={self.id}, name='{self.name}', brand='{self.brand}', price={self.price}, stock={self.stock})>"

class ChatMemoryModel(Base):
    """
    Modelo ORM para almacenar el historial de mensajes del chat.

    Mapea la tabla 'chat_memory', registrando mensajes enviados y recibidos
    durante conversaciones activas, asociados a una sesión específica.

    Attributes:
        id (int): Identificador único del mensaje (clave primaria).
        session_id (str): Identificador de la sesión de chat (no nulo e indexado).
        role (str): Rol del emisor ('user' o 'assistant').
        message (str): Texto del mensaje.
        timestamp (datetime): Momento de envío (default a utcnow).
    """

    __tablename__ = "chat_memory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' o 'assistant'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """
        Representación legible del mensaje de chat, útil para debugging.

        Returns:
            str: Cadena representativa del mensaje en la memoria de chat.
        
        Example:
            >>> print(ChatMemoryModel(id=1, session_id="abc", role="user"))
            <ChatMemoryModel(id=1, session_id='abc', role='user', timestamp=...)>
        """
        return f"<ChatMemoryModel(id={self.id}, session_id='{self.session_id}', role='{self.role}', timestamp={self.timestamp})>"

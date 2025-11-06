from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Product:
    """
    Entidad de dominio que representa un producto dentro del e-commerce.

    Contiene los datos fundamentales de un producto, así como métodos de validación
    y lógica de negocio relacionada con inventario y disponibilidad.

    Attributes:
        id (Optional[int]): Identificador único del producto, puede ser None para productos nuevos.
        name (str): Nombre del producto, campo obligatorio.
        brand (str): Marca a la que pertenece el producto.
        category (str): Categoría del producto (por ejemplo, zapatillas, ropa).
        size (str): Talla o tamaño principal.
        color (str): Color principal del producto.
        price (float): Precio, debe ser mayor a 0.
        stock (int): Cantidad disponible en inventario, no negativa.
        description (str): Descripción textual del producto.
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self):
        """
        Valida el estado inicial de la entidad Product.

        Verifica reglas de dominio, lanzando ValueError si algún campo obligatorio es inválido:
        - Nombre no vacío.
        - Precio positivo.
        - Stock no negativo.

        Raises:
            ValueError: Si algún campo no cumple las restricciones.
        """
        if not self.name or not self.name.strip():
            raise ValueError("name no puede estar vacío")
        if self.price is None or self.price <= 0:
            raise ValueError("price debe ser mayor a 0")
        if self.stock is None or self.stock < 0:
            raise ValueError("stock no puede ser negativo")

    def is_available(self) -> bool:
        """
        Indica si el producto está disponible para su compra (stock > 0).

        Returns:
            bool: True si hay stock disponible, False en caso contrario.

        Example:
            >>> p = Product(..., stock=5, ...)
            >>> p.is_available()
            True
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto en la cantidad especificada.

        Valida que la cantidad sea positiva y que haya suficiente stock.

        Args:
            quantity (int): Unidades a descontar. Debe ser positivo y no mayor al stock actual.

        Raises:
            ValueError: Si la cantidad es negativa o mayor al stock actual.

        Example:
            >>> p = Product(stock=10, ...)
            >>> p.reduce_stock(3)
            >>> print(p.stock)
            7
        """
        if quantity <= 0:
            raise ValueError("quantity debe ser positivo")
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock")
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Incrementa el stock del producto en la cantidad especificada.

        Args:
            quantity (int): Unidades a sumar al stock, debe ser positiva.

        Raises:
            ValueError: Si la cantidad es negativa o cero.

        Example:
            >>> p = Product(stock=5, ...)
            >>> p.increase_stock(2)
            >>> print(p.stock)
            7
        """
        if quantity <= 0:
            raise ValueError("quantity debe ser positivo")
        self.stock += quantity

@dataclass
class ChatMessage:
    """
    Entidad de dominio que representa un mensaje dentro de una sesión de chat.

    Incluye datos básicos de identificación, contenido y tipo de mensaje, así
    como métodos utilitarios para distinguir mensajes según su origen.

    Attributes:
        id (Optional[int]): Identificador único del mensaje.
        session_id (str): Identificador de la sesión a la que pertenece el mensaje.
        role (str): Rol emisor del mensaje, valores posibles: 'user' o 'assistant'.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Momento en que fue enviado el mensaje.
    """

    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self):
        """
        Valida los campos obligatorios al construir un mensaje de chat.

        Raises:
            ValueError: Si 'session_id', 'message' están vacíos o si 'role' no es válido.
        """
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id no puede estar vacío")
        if not self.message or not self.message.strip():
            raise ValueError("message no puede estar vacío")
        if self.role not in ("user", "assistant"):
            raise ValueError("role debe ser 'user' o 'assistant'")

    def is_from_user(self) -> bool:
        """
        Indica si el mensaje fue enviado por el usuario.

        Returns:
            bool: True si el rol es 'user', False si es 'assistant'.

        Example:
            >>> m = ChatMessage(role="user", ...)
            >>> m.is_from_user()
            True
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """
        Indica si el mensaje fue enviado por el asistente.

        Returns:
            bool: True si el rol es 'assistant', False si es 'user'.

        Example:
            >>> m = ChatMessage(role="assistant", ...)
            >>> m.is_from_assistant()
            True
        """
        return self.role == "assistant"

@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto reciente de una conversación de chat.

    Este objeto mantiene un listado de mensajes recientes, permitiendo que
    el servicio de IA pueda generar respuestas coherentes con el historial.

    Attributes:
        messages (list[ChatMessage]): Lista de mensajes recientes.
        max_messages (int): Máximo de mensajes a tomar en cuenta para el contexto.
    """

    messages: list[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> list[ChatMessage]:
        """
        Devuelve los mensajes más recientes de la conversación.

        Limita el número de mensajes según max_messages. Ordena por timestamp para coherencia.

        Returns:
            list[ChatMessage]: Lista de mensajes recientes, ordenados por timestamp.

        Example:
            >>> ctx = ChatContext([...])
            >>> recientes = ctx.get_recent_messages()
            >>> len(recientes) <= ctx.max_messages
            True
        """
        recent = self.messages[-self.max_messages:]
        return recent if len(recent) == 0 else sorted(recent, key=lambda m: m.timestamp)

    def format_for_prompt(self) -> str:
        """
        Construye una cadena formateada que representa el historial reciente para la IA.

        Alterna entre marcar los mensajes como "Usuario" o "Asistente".

        Returns:
            str: Texto listo para ser usado como parte del prompt en IA.

        Example:
            >>> ctx = ChatContext([ChatMessage(role="user", message="Hola", ...)])
            >>> prompt = ctx.format_for_prompt()
            >>> print(prompt)
            Usuario: Hola
        """
        lines = []
        for msg in self.get_recent_messages():
            role = "Usuario" if msg.is_from_user() else "Asistente"
            lines.append(f"{role}: {msg.message}")
        return "\n".join(lines)

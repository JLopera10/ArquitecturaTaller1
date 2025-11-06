# tests/conftest.py
import pytest
from datetime import datetime, timezone

# Importa las entidades reales de tu dominio
from src.domain.entities import Product, ChatMessage, ChatContext

@pytest.fixture
def sample_product():
    """
    Fixture de Pytest que genera un producto válido de ejemplo.

    Este producto puede ser usado en múltiples pruebas unitarias
    para validar comportamientos sobre productos con stock disponible.

    Returns:
        Product: Instancia válida de un producto de la entidad de dominio.

    Example:
        def test_algo(sample_product):
            assert sample_product.price > 0
    """
    return Product(
        id=None,
        name="Air Zoom Pegasus",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapato para correr con amortiguación"
    )

@pytest.fixture
def out_of_stock_product():
    """
    Fixture que genera un producto sin unidades en stock.

    Utilizado para probar funcionalidades relacionadas a agotamiento
    o indisponibilidad en inventario.

    Returns:
        Product: Instancia de un producto agotado.
    """
    return Product(
        id=None,
        name="Zapato Sin Stock",
        brand="MarcaX",
        category="Casual",
        size="40",
        color="Blanco",
        price=50.0,
        stock=0,
        description="Producto sin stock"
    )

@pytest.fixture
def sample_chat_messages():
    """
    Fixture que retorna una lista ejemplo de mensajes de chat.

    Incluye mensajes de usuario y asistente que pueden ser
    utilizados para poblar contextos de conversación en pruebas.

    Returns:
        list[ChatMessage]: Lista de dos mensajes (user y assistant).
    """
    now = datetime.now(timezone.utc)
    m1 = ChatMessage(id=None, session_id="s1", role="user", message="Hola, busco running", timestamp=now)
    m2 = ChatMessage(id=None, session_id="s1", role="assistant", message="¿Qué talla?", timestamp=now)
    return [m1, m2]

@pytest.fixture
def sample_chat_context(sample_chat_messages):
    """
    Fixture para crear un contexto de conversación basado en mensajes de ejemplo.

    Permite inicializar objetos que usen ChatContext para pruebas de IA o lógica de chat.

    Args:
        sample_chat_messages (list[ChatMessage]): Mensajes predefinidos de la sesión.

    Returns:
        ChatContext: Objeto de contexto con los mensajes cargados.
    """
    return ChatContext(messages=sample_chat_messages, max_messages=6)

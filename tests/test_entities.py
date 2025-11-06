# tests/test_entities.py
import pytest
from datetime import datetime, timezone

from src.domain.entities import Product, ChatMessage, ChatContext
from src.domain.exceptions import ProductNotFoundError, InvalidProductDataError  # si los usas

def test_product_validations_price_and_stock(sample_product):
    """
    Verifica que los campos de precio y stock de un producto sean válidos.

    Usa el fixture sample_product y valida:
      - El precio debe ser mayor a 0.
      - El stock debe ser mayor o igual a 0.
      - El nombre no puede estar vacío.
    """
    p = sample_product
    assert p.price > 0
    assert p.stock >= 0
    assert p.name != ""

def test_product_is_available_true(sample_product):
    """
    Verifica que el método is_available retorne True si hay stock disponible.
    """
    assert sample_product.is_available() is True

def test_product_is_available_false(out_of_stock_product):
    """
    Verifica que is_available retorne False si el stock es cero.
    """
    assert out_of_stock_product.is_available() is False

def test_product_reduce_stock_success(sample_product):
    """
    Prueba que reduce_stock descuente correctamente la cantidad indicada al stock.

    Valida que tras la operación, el stock sea el inicial menos la cantidad descontada.
    """
    p = sample_product
    initial_stock = p.stock
    p.reduce_stock(2)
    assert p.stock == initial_stock - 2

def test_product_reduce_stock_invalid_quantity(sample_product):
    """
    Verifica que reduce_stock lance ValueError si se intenta reducir por una cantidad negativa.
    """
    p = sample_product
    with pytest.raises(ValueError):
        p.reduce_stock(-1)  # cantidad negativa no permitida

def test_product_reduce_stock_insufficient(sample_product):
    """
    Verifica que reducir stock por encima del disponible lance ValueError.
    """
    p = sample_product
    with pytest.raises(ValueError):
        p.reduce_stock(p.stock + 1)  # pedir más que el stock

def test_product_increase_stock(sample_product):
    """
    Valida que increase_stock suma correctamente la cantidad al stock original.
    """
    p = sample_product
    initial = p.stock
    p.increase_stock(3)
    assert p.stock == initial + 3

def test_chatmessage_validations():
    """
    Prueba la validación de roles en ChatMessage y métodos de identificación de rol.

    Valida que is_from_user y is_from_assistant funcionen correctamente.
    """
    now = datetime.now(timezone.utc)
    cm = ChatMessage(id=None, session_id="sess1", role="user", message="Hola", timestamp=now)
    assert cm.is_from_user() is True
    assert cm.is_from_assistant() is False

def test_chatmessage_invalid_role_raises():
    """
    Verifica que crear un ChatMessage con rol inválido lance ValueError.
    """
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        ChatMessage(id=None, session_id="sess1", role="unknown", message="Hola", timestamp=now)

def test_chatcontext_format_for_prompt(sample_chat_context):
    """
    Valida que el método format_for_prompt de ChatContext incluya los roles en el texto.

    Asegura que los mensajes formateados contengan "Usuario" y "Asistente"
    u otra variante esperada.
    """
    ctx = sample_chat_context
    formatted = ctx.format_for_prompt()
    # Debe contener las partes del historial en el formato esperado.
    assert "Usuario" in formatted or "user" in formatted.lower()
    assert "Asistente" in formatted or "assistant" in formatted.lower()

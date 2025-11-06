# tests/test_services.py
import pytest
from datetime import datetime, timezone

from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.domain.entities import Product, ChatMessage, ChatContext

# --- Mocks para repositorios y servicios IA ----------------------------------------

class FakeProductRepository:
    """
    Mock simple de repositorio de productos para usar en pruebas de servicios.
    Permite gestionar productos en memoria sin acceso a la base real.
    """
    def __init__(self, products=None):
        self._products = products or []

    def get_all(self):
        return list(self._products)

    def get_by_id(self, product_id):
        for p in self._products:
            if p.id == product_id:
                return p
        return None

    def save(self, product):
        if product.id is None:
            product.id = len(self._products) + 1
            self._products.append(product)
        else:
            for i, existing in enumerate(self._products):
                if existing.id == product.id:
                    self._products[i] = product
                    break
        return product

    def delete(self, product_id):
        before = len(self._products)
        self._products = [p for p in self._products if p.id != product_id]
        return len(self._products) < before

class FakeChatRepository:
    """
    Mock simple de repositorio de chat para pruebas de servicios de mensajería.
    Mantiene los mensajes en una lista de memoria.
    """
    def __init__(self):
        self._messages = []

    def save_message(self, message: ChatMessage):
        message.id = len(self._messages) + 1
        self._messages.append(message)
        return message

    def get_recent_messages(self, session_id: str, count: int):
        msgs = [m for m in self._messages if m.session_id == session_id]
        return msgs[-count:] if count else msgs

    def get_session_history(self, session_id: str, limit=None):
        msgs = [m for m in self._messages if m.session_id == session_id]
        if limit:
            return msgs[-limit:]
        return msgs

    def delete_session_history(self, session_id: str):
        before = len(self._messages)
        self._messages = [m for m in self._messages if m.session_id != session_id]
        return before - len(self._messages)

class FakeGeminiService:
    """
    Mock de servicio Gemini que simula respuestas de IA de manera determinista.
    """
    async def generate_response(self, user_message: str, products, context: ChatContext):
        return f"Respuesta simulada a: {user_message}"

# --- Fixtures para servicios ------------------------------------------------------

@pytest.fixture
def product_service_fixture():
    """
    Fixture que retorna una instancia de ProductService con un repositorio simulado
    inicializado con dos productos diferentes.
    """
    p1 = Product(id=1, name="A", brand="B", category="Running", size="42", color="N", price=100.0, stock=2, description="d")
    p2 = Product(id=2, name="C", brand="D", category="Casual", size="40", color="B", price=80.0, stock=0, description="d")
    repo = FakeProductRepository(products=[p1, p2])
    service = ProductService(repo)
    return service, repo

@pytest.fixture
def chat_service_fixture():
    """
    Fixture que inicializa un ChatService con repositorios y servicio IA simulados, listos para pruebas.
    """
    prod_repo = FakeProductRepository(products=[])
    chat_repo = FakeChatRepository()
    ai = FakeGeminiService()
    service = ChatService(prod_repo, chat_repo, ai)
    return service, prod_repo, chat_repo, ai

# --- Tests ProductService ---------------------------------------------------------

def test_productservice_get_all(product_service_fixture):
    """
    Valida que get_all_products retorne una lista con la cantidad correcta de productos.
    """
    service, repo = product_service_fixture
    prods = service.get_all_products()
    assert isinstance(prods, list)
    assert len(prods) == 2

def test_productservice_create_and_delete(product_service_fixture):
    """
    Prueba la creación de un nuevo producto y su posterior eliminación.
    """
    service, repo = product_service_fixture
    dto = ProductDTO(name="Nuevo", brand="X", category="Run", size="41", color="G", price=60.0, stock=3, description="nuevo")
    created = service.create_product(dto)
    assert created.id is not None
    ok = service.delete_product(created.id)
    assert ok is True

def test_productservice_get_product_by_id_raises(product_service_fixture):
    """
    Verifica que obtener un producto inexistente lanza la excepción esperada.
    """
    service, repo = product_service_fixture
    with pytest.raises(Exception):
        service.get_product_by_id(9999)  # id inexistente, debe lanzar excepción

# --- Tests ChatService ------------------------------------------------------------

import asyncio

@pytest.mark.asyncio
async def test_chatservice_process_message(chat_service_fixture):
    """
    Prueba la recepción y respuesta de un mensaje por parte del ChatService usando mocks.
    Comprueba que el mensaje de usuario y respuesta del asistente quedan registrados.
    """
    service, prod_repo, chat_repo, ai = chat_service_fixture
    req = ChatMessageRequestDTO(session_id="s1", message="Hola, busco zapatos")
    resp = await service.process_message(req)
    assert "assistant_message" in resp.__dict__ or hasattr(resp, "assistant_message")
    history = chat_repo.get_session_history("s1")
    assert len(history) >= 2  # user + assistant

@pytest.mark.asyncio
async def test_chatservice_handles_ai_error(chat_service_fixture, monkeypatch):
    """
    Simula un fallo del servicio IA y valida que se propaga la excepción correctamente.
    """
    service, prod_repo, chat_repo, ai = chat_service_fixture

    async def fail_generate(user_message, products, context):
        raise RuntimeError("AI failure")

    monkeypatch.setattr(ai, "generate_response", fail_generate)
    req = ChatMessageRequestDTO(session_id="s2", message="Esto provocará error")
    with pytest.raises(Exception):
        await service.process_message(req)

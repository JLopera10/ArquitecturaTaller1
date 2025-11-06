from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.db.init_data import load_initial_data
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)
from src.domain.exceptions import ProductNotFoundError, ChatServiceError

# ----------------------------------------------------------
# Inicialización de la aplicación
# ----------------------------------------------------------
app = FastAPI(
    title="E-commerce Chat AI API",
    description="API del asistente virtual para ventas de zapatos con integración IA (Gemini).",
    version="1.0.0",
)

# ----------------------------------------------------------
# Configuración de CORS
# ----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir a tu dominio si quieres
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# Evento de inicio
# ----------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """
    Inicializa la base de datos y carga los datos al arrancar la aplicación.

    Esta función se ejecuta automáticamente en el arranque del servidor FastAPI.
    Llama a la creación de tablas y la carga de datos iniciales si la base de datos está vacía.

    Returns:
        None

    Note:
        No requiere argumentos. Debe ejecutarse antes de aceptar peticiones.
    """
    init_db()
    load_initial_data()

# ----------------------------------------------------------
# Endpoint raíz
# ----------------------------------------------------------
@app.get("/")
def root():
    """
    Proporciona información básica y resumen de los endpoints de la API.

    Returns:
        dict: Información de la aplicación y rutas expuestas.
    """
    return {
        "app": "E-commerce Chat AI",
        "version": "1.0.0",
        "description": "Asistente virtual para tienda de zapatos impulsado por Gemini AI.",
        "endpoints": [
            "/products",
            "/products/{product_id}",
            "/chat",
            "/chat/history/{session_id}",
            "/health",
        ],
    }

# ----------------------------------------------------------
# GET /products
# ----------------------------------------------------------
@app.get("/products", response_model=List[ProductDTO])
def get_products(db: Session = Depends(get_db)):
    """
    Lista todos los productos disponibles en la tienda.

    Args:
        db (Session): Sesión de base de datos inyectada por FastAPI.

    Returns:
        List[ProductDTO]: Listado completo de productos registrados.

    Example:
        GET /products
    """
    repo = SQLProductRepository(db)
    service = ProductService(repo)
    return service.get_all_products()

# ----------------------------------------------------------
# GET /products/{product_id}
# ----------------------------------------------------------
@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un producto a partir de su ID.

    Args:
        product_id (int): Identificador único del producto.
        db (Session): Sesión de base de datos.

    Returns:
        ProductDTO: Detalle del producto encontrado.

    Raises:
        HTTPException: 404 si el producto no existe.

    Example:
        GET /products/10
    """
    repo = SQLProductRepository(db)
    service = ProductService(repo)
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail=f"Producto con ID {product_id} no encontrado.")

# ----------------------------------------------------------
# POST /chat
# ----------------------------------------------------------
@app.post("/chat", response_model=ChatMessageResponseDTO)
async def process_chat_message(
    request: ChatMessageRequestDTO, db: Session = Depends(get_db)
):
    """
    Procesa un mensaje enviado por el usuario y retorna la respuesta de la IA.

    Orquesta la interacción entre el usuario y el asistente virtual,
    almacenando el intercambio y usando Gemini AI para responder de manera contextual.

    Args:
        request (ChatMessageRequestDTO): Mensaje y sesión enviados por el usuario.
        db (Session): Sesión de base de datos.

    Returns:
        ChatMessageResponseDTO: Respuesta generada por la IA.

    Raises:
        HTTPException: 500 si ocurre un error en el proceso.

    Example:
        POST /chat (body con session_id y message)
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai_service = GeminiService()
    chat_service = ChatService(product_repo, chat_repo, ai_service)

    try:
        response = await chat_service.process_message(request)
        return response
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ----------------------------------------------------------
# GET /chat/history/{session_id}
# ----------------------------------------------------------
@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(
    session_id: str,
    limit: int = Query(10, description="Cantidad máxima de mensajes a obtener."),
    db: Session = Depends(get_db),
):
    """
    Recupera el historial de conversación de una sesión de usuario.

    Args:
        session_id (str): Identificador de la sesión.
        limit (int): Número máximo de mensajes a retornar.
        db (Session): Sesión de base de datos.

    Returns:
        List[ChatHistoryDTO]: Lista de mensajes en orden cronológico de esa sesión.

    Raises:
        HTTPException: 500 si ocurre un error en el servicio.

    Example:
        GET /chat/history/user1?limit=10
    """
    chat_repo = SQLChatRepository(db)
    product_repo = SQLProductRepository(db)
    ai_service = GeminiService()
    chat_service = ChatService(product_repo, chat_repo, ai_service)

    try:
        history = chat_service.get_session_history(session_id, limit)
        return history
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------
# DELETE /chat/history/{session_id}
# ----------------------------------------------------------
@app.delete("/chat/history/{session_id}")
def clear_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Elimina todos los mensajes del historial de una sesión específica.

    Args:
        session_id (str): Identificador de la sesión de chat.
        db (Session): Sesión de base de datos.

    Returns:
        dict: Cantidad de mensajes eliminados bajo la clave 'deleted_messages'.

    Raises:
        HTTPException: 500 si ocurre algún fallo en el proceso.

    Example:
        DELETE /chat/history/user1
    """
    chat_repo = SQLChatRepository(db)
    product_repo = SQLProductRepository(db)
    ai_service = GeminiService()
    chat_service = ChatService(product_repo, chat_repo, ai_service)

    try:
        deleted = chat_service.clear_session_history(session_id)
        return {"deleted_messages": deleted}
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------
# GET /health
# ----------------------------------------------------------
@app.get("/health")
def health_check():
    """
    Endpoint de verificación para monitorear el estado de la API.

    Returns:
        dict: Estado actual y timestamp de respuesta.

    Example:
        GET /health
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow(),
    }

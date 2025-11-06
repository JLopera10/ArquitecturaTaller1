from datetime import datetime, timezone
from typing import List, Optional

from src.domain.entities import ChatMessage, ChatContext
from src.domain.repositories import IChatRepository, IProductRepository
from src.domain.exceptions import ChatServiceError
from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)

class ChatService:
    """
    Servicio de aplicación para gestionar el chat con IA.

    Este servicio orquesta la interacción entre el repositorio de productos,
    el repositorio de chat y el servicio de IA (como Gemini) para proporcionar
    respuestas contextuales a los usuarios durante una conversación.

    Attributes:
        product_repository (IProductRepository): Repositorio de productos.
        chat_repository (IChatRepository): Repositorio de mensajes de chat.
        ai_service: Servicio de IA (por ejemplo, GeminiService).
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service,
    ):
        """
        Inicializa el ChatService con las dependencias requeridas.

        Args:
            product_repository (IProductRepository): Acceso a los productos.
            chat_repository (IChatRepository): Manejo del historial de mensajes.
            ai_service: Servicio de IA que genera respuestas automáticas.
        """
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    # ------------------------------------------------------------------
    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y genera una respuesta con IA.

        Este método realiza el flujo completo:
            1. Obtiene productos disponibles.
            2. Recupera historial de conversación reciente.
            3. Genera contexto y envía el mensaje al servicio de IA.
            4. Guarda el mensaje del usuario y la respuesta del asistente.
            5. Retorna la respuesta como un DTO.

        Args:
            request (ChatMessageRequestDTO): Mensaje del usuario con session_id.

        Returns:
            ChatMessageResponseDTO: Respuesta generada por la IA junto con timestamp.

        Raises:
            ChatServiceError: Si ocurre un error al procesar el mensaje
                o comunicarse con el servicio de IA.

        Example:
            >>> request = ChatMessageRequestDTO(
            ...     session_id="user123",
            ...     message="Busco zapatos Nike"
            ... )
            >>> response = await chat_service.process_message(request)
            >>> print(response.assistant_message)
            "Tengo varios modelos Nike disponibles..."
        """
        try:
            # 1️⃣ Obtener todos los productos
            products = self.product_repository.get_all()

            # 2️⃣ Obtener historial reciente (últimos 6 mensajes)
            recent_history = self.chat_repository.get_recent_messages(
                request.session_id, count=6
            )

            # 3️⃣ Crear contexto del chat
            context = ChatContext(messages=recent_history)

            # 4️⃣ Llamar al servicio de IA
            ai_response = await self.ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            # 5️⃣ Guardar mensaje del usuario
            user_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=datetime.now(timezone.utc),
            )
            self.chat_repository.save_message(user_msg)

            # 6️⃣ Guardar respuesta del asistente
            assistant_msg = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=ai_response,
                timestamp=datetime.now(timezone.utc),
            )
            self.chat_repository.save_message(assistant_msg)

            # 7️⃣ Retornar respuesta formateada como DTO
            response_dto = ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_response,
                timestamp=assistant_msg.timestamp,
            )

            return response_dto

        except Exception as e:
            raise ChatServiceError(str(e))

    # ------------------------------------------------------------------
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial de mensajes de una sesión de chat.

        Si 'limit' está definido, retorna solo los últimos N mensajes;
        en caso contrario, retorna el historial completo de la sesión.

        Args:
            session_id (str): Identificador de la sesión de chat.
            limit (Optional[int]): Número máximo de mensajes a retornar.

        Returns:
            List[ChatHistoryDTO]: Lista de mensajes del historial solicitados.

        Raises:
            ChatServiceError: Si ocurre un error al acceder al historial.

        Example:
            >>> history = chat_service.get_session_history("user123", limit=10)
            >>> print(len(history))
            10
        """
        try:
            history = self.chat_repository.get_session_history(session_id, limit)
            return [ChatHistoryDTO.model_validate(msg) for msg in history]
        except Exception as e:
            raise ChatServiceError(f"Error al obtener historial: {str(e)}")

    # ------------------------------------------------------------------
    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión de chat.

        Retorna la cantidad de mensajes eliminados de la sesión.

        Args:
            session_id (str): Identificador de la sesión de chat.

        Returns:
            int: Número de mensajes eliminados.

        Raises:
            ChatServiceError: Si ocurre un error al borrar el historial.

        Example:
            >>> eliminados = chat_service.clear_session_history("user123")
            >>> print(eliminados)
            12
        """
        try:
            deleted = self.chat_repository.delete_session_history(session_id)
            return deleted
        except Exception as e:
            raise ChatServiceError(f"Error al limpiar historial: {str(e)}")

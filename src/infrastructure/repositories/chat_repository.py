from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel

class SQLChatRepository(IChatRepository):
    """
    Implementación concreta de IChatRepository utilizando SQLAlchemy.

    Permite almacenar y recuperar mensajes de chat desde la base de datos relacional,
    cumpliendo con la interfaz de repositorio para la capa de dominio.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy para realizar consultas y operaciones.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión SQLAlchemy inyectada.

        Args:
            db (Session): Sesión activa para operaciones sobre la base de datos.
        """
        self.db = db

    # ------------------------------------------------------------------
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Almacena un mensaje en la base de datos y retorna la entidad persistida.

        Args:
            message (ChatMessage): Mensaje de chat a guardar.

        Returns:
            ChatMessage: Instancia del mensaje almacenado (con ID generado por la base).

        Example:
            >>> repo.save_message(ChatMessage(...))
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    # ------------------------------------------------------------------
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Recupera el historial completo de mensajes de una sesión.

        Si el parámetro limit está definido, retorna solo los últimos N mensajes,
        en orden cronológico (más antiguos primero).

        Args:
            session_id (str): ID de la sesión de chat.
            limit (Optional[int]): Número máximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Lista de mensajes encontrados.

        Example:
            >>> repo.get_session_history("user123", limit=5)
        """
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(desc(ChatMemoryModel.timestamp))
        )

        if limit:
            query = query.limit(limit)

        models = query.all()
        models.reverse()  # Invertimos para obtener los más antiguos primero
        return [self._model_to_entity(m) for m in models]

    # ------------------------------------------------------------------
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de la sesión especificada.

        Args:
            session_id (str): Identificador de la sesión de chat.

        Returns:
            int: Cantidad de mensajes eliminados.

        Example:
            >>> repo.delete_session_history("abc")
        """
        models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .all()
        )
        deleted_count = len(models)
        for m in models:
            self.db.delete(m)
        self.db.commit()
        return deleted_count

    # ------------------------------------------------------------------
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Recupera los últimos N mensajes de una sesión, ordenados de más antiguo a más reciente.

        Args:
            session_id (str): Identificador de la sesión de chat.
            count (int): Número máximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Lista de los N mensajes recientes.

        Example:
            >>> repo.get_recent_messages("user123", count=3)
        """
        query = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(desc(ChatMemoryModel.timestamp))
            .limit(count)
        )
        models = query.all()
        models.reverse()  # Para devolverlos en orden cronológico (más antiguos primero)
        return [self._model_to_entity(m) for m in models]

    # ------------------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------------------
    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte una instancia de ChatMemoryModel (ORM) a ChatMessage (dominio).

        Args:
            model (ChatMemoryModel): Modelo ORM a transformar.

        Returns:
            ChatMessage: Entidad del dominio equivalente.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad ChatMessage (dominio) a un modelo ORM ChatMemoryModel.

        Args:
            entity (ChatMessage): Entidad de dominio a transformar.

        Returns:
            ChatMemoryModel: Modelo ORM equivalente.
        """
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )

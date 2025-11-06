from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# ----------------------------------------------------------
# Configuración del motor de base de datos
# ----------------------------------------------------------
# Carpeta donde se guardará la base de datos (por si no existe)
os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"

# Para SQLite: se recomienda check_same_thread=False para multithread con ORM
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creador de sesiones (Session factory)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Clase base para los modelos ORM
Base = declarative_base()


# ----------------------------------------------------------
# Dependencia para FastAPI o cualquier consumo manual
# ----------------------------------------------------------
def get_db():
    """
    Generador de sesiones de base de datos SQLAlchemy para FastAPI y otros usos.

    Esta función se utiliza como dependencia para inyección en endpoints, asegurando 
    que la sesión de base de datos se cierre correctamente después del uso.

    Yields:
        Session: Sesión activa para la base de datos, de tipo SQLAlchemy.

    Example:
        with next(get_db()) as db:
            # usar db aquí
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------------------------
# Inicializador de la base de datos
# ----------------------------------------------------------
def init_db():
    """
    Inicializa la base de datos creando todas las tablas ORM necesarias.

    Importa los modelos y ejecuta el mapeo para garantizar que la base de datos contenga
    todas las tablas fundamentales según las definiciones de los modelos ORM.

    Returns:
        None

    Note:
        Esta función debe ser llamada en el evento de startup de la aplicación o durante el setup inicial.
    """
    from src.infrastructure.db import models  # Importa los modelos antes de crear las tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente en ./data/ecommerce_chat.db")

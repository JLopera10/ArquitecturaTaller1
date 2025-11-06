Juan Manuel Lopera Soto
E-commerce Chat AI API
Descripción del proyecto

Sistema de backend para un e-commerce de calzado, con asistente virtual potenciado por IA (Google Gemini) que guía a los usuarios, responde consultas, recomienda productos y administra el catálogo de manera sencilla por medio de endpoints robustos y documentados.
Características principales

    Catálogo robusto de productos (CRUD completo)

    Asistente conversacional inteligente (IA Gemini)

    Gestión de historial y contexto conversacional para respuestas personalizadas

    Validación exhaustiva y manejo de excepciones de negocio

    Pruebas unitarias y de integración listas para CI

    Documentación detallada y endpoints siguiendo buenas prácticas REST

Arquitectura

El sistema sigue una arquitectura de capas:

    Presentación/API: FastAPI expone los endpoints.

    Aplicación: Orquesta la lógica de negocio y flujos principales.

    Dominio: Entidades, DTOs, repositorios, servicios, reglas y excepciones propias del negocio.

    Infraestructura: Acceso a base de datos (SQLAlchemy), proveedores externos (Gemini IA).

Diagrama

                 +-------------+
                 |    Cliente  |
                 +------+------+ 
                        |
      REST API (FastAPI)|
                        v
  +-------------------------+
  |         Aplicación      |
  +-------------------------+
      |       |       |
      v       v       v
 Entidades  Servicios  Repositorios
      |       |       |
      +---------------------+
                |
        Infraestructura (DB, Gemini)

Instalación

    Clonar el repositorio

bash
git clone https://github.com/JLopera10/ArquitecturaTaller1
cd ArquitecturaTaller1

Crear y activar un entorno virtual

bash
python -m venv venv
source venv/bin/activate   # o venv\Scripts\activate en Windows

Instalar dependencias

    pip install -r requirements.txt

Configuración

    Variables de entorno (.env):

    Crear un archivo .env en la raíz con:

GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development

Inicializar la base de datos y cargar datos de ejemplo (opcional):

    docker compose build (Lo hace automaticamente)

Uso

Ejecutar la API localmente:

uvicorn src.main:app --reload

Ejemplos de endpoints

    GET /products
    Lista todos los productos disponibles.

    GET /products/{product_id}
    Devuelve detalles de un producto específico.

    POST /chat
    Envía un mensaje de usuario y recibe respuesta del asistente.

    json
    {
      "session_id": "abc123",
      "message": "¿Qué zapatillas Nike tiene disponibles?"
    }

    GET /chat/history/{session_id}
    Historial conversacional por sesión.

    DELETE /chat/history/{session_id}
    Borra el historial de una sesión.

    GET /health
    Verifica el estado de la API.

Testing

Corre los tests con Pytest:

pytest

Ver coverages:

coverage run -m pytest
coverage report -m

Opcionalmente puedes filtrar por archivos, clases o funciones específicas.
Docker

    Construir el contenedor

docker compose build

Ejecutar el contenedor

docker compose up

Esto levantará la API en http://localhost:8000
Tecnologías utilizadas

    Python 3.10+

    FastAPI (API REST)

    SQLAlchemy (ORM y acceso a SQLite)

    Google Generative AI (Gemini)

    Pytest (pruebas)

    Docker (despliegue/portabilidad)

    Pydantic (modelos y validación)

    dotenv (manejo de variables de entorno)

Estructura del proyecto

data/
├── ecommerce_chat.db
└── ecommerce.db
src/
├── application/       
│   ├── chat_service.py
│   ├── dtos.py
│   └── product_service.py
├── domain/             
│   ├── entities.py
│   ├── exceptions.py
│   └── repositories.py
├── infrastructure/     
│   ├── api/
│   │   └── main.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── init_data.py
│   ├── repositories/
│   │   ├── product_repository.py
│   │   └── chat_repository.py
│   └── llm_providers/
│       └── gemini_service.py          
└── ...
tests/
├── conftest.py
├── test_entities.py
└── test_services.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from src.domain.exceptions import ChatServiceError

load_dotenv()  # Carga variables desde .env si existen

class GeminiService:
    """
    Servicio para integrarse con la API de Gemini (Google Generative AI).

    Este servicio permite enviar prompts a Gemini para obtener respuestas inteligentes,
    contextuales y adaptadas al dominio de ventas de zapatos.
    """

    def __init__(self):
        """
        Inicializa el servicio Gemini configurando la clave API y el modelo usado.

        - Lee la variable de entorno GEMINI_API_KEY.
        - Levanta una excepción si no está configurada.
        - Prepara el modelo 'gemini-2.5-flash' para futuras consultas.

        Raises:
            ChatServiceError: Si no está definida la clave GEMINI_API_KEY.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ChatServiceError("No se encontró GEMINI_API_KEY en las variables de entorno.")

        # Configurar cliente
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    # ------------------------------------------------------------------
    async def generate_response(self, user_message, products, context):
        """
        Genera una respuesta textual utilizando Gemini, basada en el mensaje de usuario,
        el catálogo actual de productos y el contexto conversacional previo.

        Args:
            user_message (str): Texto ingresado por el usuario, a resolver con IA.
            products (list): Lista de productos disponibles actualmente.
            context: Objeto que encapsula el contexto/conversación reciente.

        Returns:
            str: Respuesta generada por Gemini (limpia de espacios extremos).

        Raises:
            ChatServiceError: Si falla la obtención de la respuesta por IA.

        Example:
            >>> respuesta = await gemini_service.generate_response("¿Qué zapatillas hay en stock?", productos, ctx)
            >>> print(respuesta)
        """
        try:
            # 1️⃣ Formatear lista de productos
            products_text = self.format_products_info(products)

            # 2️⃣ Formatear contexto conversacional
            context_text = context.format_for_prompt() if context else "No hay mensajes previos."

            # 3️⃣ Construir prompt completo
            prompt = f"""
Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

PRODUCTOS DISPONIBLES:
{products_text}

INSTRUCCIONES:
- Sé amigable y profesional
- Usa el contexto de la conversación anterior
- Recomienda productos específicos cuando sea apropiado
- Menciona precios, tallas y disponibilidad
- Si no tienes información, sé honesto

CONVERSACIÓN ANTERIOR:
{context_text}

Usuario: {user_message}

Asistente:
"""

            # 4️⃣ Llamar a Gemini API
            response = await self._generate_text(prompt)

            # 5️⃣ Retornar respuesta generada
            return response.strip()

        except Exception as e:
            raise ChatServiceError(f"Error al generar respuesta de Gemini: {str(e)}")

    # ------------------------------------------------------------------
    async def _generate_text(self, prompt: str) -> str:
        """
        Realiza una llamada asincrónica a la API de Gemini y obtiene el texto de respuesta.

        Args:
            prompt (str): Texto que define el contexto, productos y mensaje del usuario.

        Returns:
            str: Texto de la respuesta generada por Gemini.

        Raises:
            ChatServiceError: Si ocurre un error al llamar la API.

        Example:
            >>> respuesta = await self._generate_text(prompt)
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text if response and response.text else "No se pudo generar una respuesta."
        except Exception as e:
            raise ChatServiceError(f"Error en la API de Gemini: {str(e)}")

    # ------------------------------------------------------------------
    def format_products_info(self, products) -> str:
        """
        Formatea una lista de productos en un texto legible para incluir en el prompt de Gemini.

        El formato generado es: "- Nombre | Marca | Precio | Stock"

        Args:
            products (list): Lista de objetos producto a formatear.

        Returns:
            str: Cadena de texto representando los productos disponibles, o aviso si vacío.

        Example:
            >>> texto = self.format_products_info(lista_productos)
            >>> print(texto)
            - Nike Pegasus | Nike | $120.00 | Stock: 10
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines = []
        for p in products:
            try:
                lines.append(f"- {p.name} | {p.brand} | ${p.price:.2f} | Stock: {p.stock}")
            except AttributeError:
                # Por si viene un modelo ORM o dict
                name = getattr(p, "name", "Desconocido")
                brand = getattr(p, "brand", "N/A")
                price = getattr(p, "price", 0.0)
                stock = getattr(p, "stock", 0)
                lines.append(f"- {name} | {brand} | ${price:.2f} | Stock: {stock}")
        return "\n".join(lines)

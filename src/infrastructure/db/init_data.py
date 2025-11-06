from src.infrastructure.db.database import SessionLocal, init_db
from src.infrastructure.db.models import ProductModel

def load_initial_data():
    """
    Carga los datos iniciales de productos en la base de datos si está vacía.

    Esta función verifica si hay productos ya registrados en la base. Si la base está vacía,
    inserta 10 productos de ejemplo con distintas marcas, categorías y características para permitir pruebas,
    demostraciones o un arranque funcional del sistema.

    Returns:
        None

    Note:
        - Si se ejecuta más de una vez y ya hay datos, NO se duplican productos.
        - Muestra mensajes informativos sobre el proceso en consola.
    """
    # Inicializa la base (crea tablas si no existen)
    init_db()

    session = SessionLocal()
    try:
        # Verificar si ya existen productos
        product_count = session.query(ProductModel).count()
        if product_count > 0:
            print(f"ℹ️ Ya existen {product_count} productos en la base de datos. No se cargaron datos nuevos.")
            return

        # Crear productos de ejemplo
        products = [
            ProductModel(
                name="Nike Air Zoom Pegasus 39",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=120.0,
                stock=15,
                description="Zapatillas ligeras y cómodas para corredores exigentes.",
            ),
            ProductModel(
                name="Adidas Ultraboost 22",
                brand="Adidas",
                category="Running",
                size="41",
                color="Blanco",
                price=180.0,
                stock=10,
                description="Amortiguación superior y diseño moderno.",
            ),
            ProductModel(
                name="Puma Smash V2",
                brand="Puma",
                category="Casual",
                size="43",
                color="Azul",
                price=70.0,
                stock=20,
                description="Estilo clásico con toque urbano, perfecto para el día a día.",
            ),
            ProductModel(
                name="Converse Chuck Taylor All Star",
                brand="Converse",
                category="Casual",
                size="42",
                color="Rojo",
                price=60.0,
                stock=25,
                description="Las icónicas zapatillas de lona que nunca pasan de moda.",
            ),
            ProductModel(
                name="New Balance 574 Core",
                brand="New Balance",
                category="Casual",
                size="44",
                color="Gris",
                price=85.0,
                stock=18,
                description="Comodidad y diseño retro con materiales de alta calidad.",
            ),
            ProductModel(
                name="Reebok Nano X3",
                brand="Reebok",
                category="Training",
                size="42",
                color="Negro",
                price=130.0,
                stock=12,
                description="Diseñadas para entrenamientos intensos, duraderas y estables.",
            ),
            ProductModel(
                name="Under Armour HOVR Sonic 5",
                brand="Under Armour",
                category="Running",
                size="40",
                color="Gris",
                price=140.0,
                stock=8,
                description="Tecnología HOVR que brinda retorno de energía y confort.",
            ),
            ProductModel(
                name="Vans Old Skool",
                brand="Vans",
                category="Casual",
                size="41",
                color="Negro",
                price=75.0,
                stock=30,
                description="Estilo skater clásico con suela waffle resistente.",
            ),
            ProductModel(
                name="Clarks Tilden Cap",
                brand="Clarks",
                category="Formal",
                size="43",
                color="Café",
                price=110.0,
                stock=9,
                description="Zapatos elegantes de cuero ideales para oficina o eventos.",
            ),
            ProductModel(
                name="Timberland Premium 6-Inch Boot",
                brand="Timberland",
                category="Outdoor",
                size="44",
                color="Beige",
                price=200.0,
                stock=6,
                description="Botas resistentes al agua, perfectas para aventuras al aire libre.",
            ),
        ]

        # Insertar todos los productos
        session.add_all(products)
        session.commit()
        print("✅ Datos iniciales cargados exitosamente (10 productos insertados).")

    except Exception as e:
        session.rollback()
        print(f"❌ Error al cargar datos iniciales: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    """
    Permite cargar los datos iniciales ejecutando este módulo como script.

    Example:
        python -m src.infrastructure.db.init_data
    """
    load_initial_data()

from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError
from src.infrastructure.db.models import ProductModel

class SQLProductRepository(IProductRepository):
    """
    Implementación concreta de IProductRepository usando SQLAlchemy.

    Este repositorio traduce entre entidades de dominio (Product) y modelos ORM,
    persistiendo y consultando información de productos desde la base relacional.

    Attributes:
        db (Session): Sesión activa de SQLAlchemy para ejecutar operaciones sobre la base.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión SQLAlchemy inyectada externamente.

        Args:
            db (Session): Sesión activa para consultas y transacciones.
        """
        self.db = db

    # ------------------------------------------------------------------
    def get_all(self) -> List[Product]:
        """
        Recupera todos los productos registrados en la base de datos.

        Returns:
            List[Product]: Lista de instancias Product encontradas.

        Example:
            >>> lista = repo.get_all()
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    # ------------------------------------------------------------------
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto a partir de su identificador único.

        Args:
            product_id (int): ID del producto a consultar.

        Returns:
            Optional[Product]: Producto encontrado, o None si no existe.

        Example:
            >>> producto = repo.get_by_id(10)
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model:
            return self._model_to_entity(model)
        return None

    # ------------------------------------------------------------------
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera todos los productos que pertenecen a una marca específica.

        Args:
            brand (str): Marca (puede ser parcial, búsqueda insensible a mayúsculas).

        Returns:
            List[Product]: Productos que cumplen con la marca indicada.

        Example:
            >>> nike = repo.get_by_brand("Nike")
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.brand.ilike(f"%{brand}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    # ------------------------------------------------------------------
    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera todos los productos de una categoría específica.

        Args:
            category (str): Nombre o parte relevante de la categoría.

        Returns:
            List[Product]: Productos que pertenecen a la categoría.

        Example:
            >>> running = repo.get_by_category("Running")
        """
        models = (
            self.db.query(ProductModel)
            .filter(ProductModel.category.ilike(f"%{category}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    # ------------------------------------------------------------------
    def save(self, product: Product) -> Product:
        """
        Guarda un producto nuevo o actualiza uno existente en la base de datos.

        Si el producto tiene ID, se actualiza el registro, si no tiene, crea uno nuevo.

        Args:
            product (Product): Entidad del dominio a persistir.

        Returns:
            Product: Entidad persistida, con el ID asignado si fue recién creada.

        Raises:
            ProductNotFoundError: Si se intenta actualizar un producto inexistente.

        Example:
            >>> nuevo = Product(...)
            >>> repo.save(nuevo)
        """
        if product.id is not None:
            # Buscar si existe
            model = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
            if not model:
                raise ProductNotFoundError(product.id)

            # Actualizar campos
            model.name = product.name
            model.brand = product.brand
            model.category = product.category
            model.size = product.size
            model.color = product.color
            model.price = product.price
            model.stock = product.stock
            model.description = product.description
        else:
            # Crear nuevo producto
            model = self._entity_to_model(product)
            self.db.add(model)

        self.db.commit()
        self.db.refresh(model)  # Actualiza el ID si fue recién creado
        return self._model_to_entity(model)

    # ------------------------------------------------------------------
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto existente por su identificador único.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto existía y fue eliminado, False si no existía.

        Example:
            >>> repo.delete(8)
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    # ------------------------------------------------------------------
    # Métodos auxiliares de conversión
    # ------------------------------------------------------------------
    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte una instancia ORM (ProductModel) a una entidad de dominio Product.

        Args:
            model (ProductModel): Instancia ORM a transformar.

        Returns:
            Product: Entidad de dominio equivalente.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """
        Convierte una entidad de dominio Product a un modelo ORM ProductModel.

        Args:
            entity (Product): Entidad de dominio a transformar.

        Returns:
            ProductModel: Modelo ORM equivalente.
        """
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )

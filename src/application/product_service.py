from typing import List, Dict
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError, InvalidProductDataError
from src.application.dtos import ProductDTO

class ProductService:
    """
    Servicio de aplicación para manejar operaciones sobre productos.

    Esta clase orquesta la lógica entre la capa de dominio y los repositorios,
    permitiendo gestionar productos de manera centralizada desde la capa de aplicación.

    Attributes:
        product_repository (IProductRepository): Repositorio de productos.
    """

    def __init__(self, product_repository: IProductRepository):
        """
        Inicializa el ProductService con el repositorio de productos inyectado.

        Args:
            product_repository (IProductRepository): Fuente de datos de productos.
        """
        self.product_repository = product_repository

    # ------------------------------------------------------------------
    def get_all_products(self) -> List[ProductDTO]:
        """
        Obtiene todos los productos registrados en el sistema.

        Returns:
            List[ProductDTO]: Lista de productos existentes.
        
        Example:
            >>> productos = product_service.get_all_products()
            >>> len(productos)
            8
        """
        products = self.product_repository.get_all()
        return [ProductDTO.model_validate(p) for p in products]

    # ------------------------------------------------------------------
    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Busca y retorna un producto basado en su identificador único.

        Args:
            product_id (int): Identificador del producto a buscar.

        Returns:
            ProductDTO: Producto encontrado.

        Raises:
            ProductNotFoundError: Si no existe el producto solicitado.
        
        Example:
            >>> producto = product_service.get_product_by_id(1)
            >>> print(producto.name)
            'Nike Air Foamposite'
        """
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        return ProductDTO.model_validate(product)

    # ------------------------------------------------------------------
    def search_products(self, filters: Dict[str, str]) -> List[ProductDTO]:
        """
        Busca productos que cumplan con filtros específicos de marca y categoría.

        Soporta los filtros: 'brand' (marca) y 'category' (categoría).

        Args:
            filters (Dict[str, str]): Diccionario con los criterios de búsqueda.

        Returns:
            List[ProductDTO]: Lista de productos que cumplen los filtros.

        Example:
            >>> filtros = {'brand': 'Nike', 'category': 'tenis'}
            >>> resultados = product_service.search_products(filtros)
            >>> len(resultados)
            3
        """
        brand = filters.get("brand")
        category = filters.get("category")

        products = self.product_repository.get_all()

        if brand:
            products = [p for p in products if p.brand.lower() == brand.lower()]
        if category:
            products = [p for p in products if p.category.lower() == category.lower()]

        return [ProductDTO.model_validate(p) for p in products]

    # ------------------------------------------------------------------
    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """
        Crea y registra un nuevo producto en el sistema.

        Args:
            product_dto (ProductDTO): Datos del producto a crear.

        Returns:
            ProductDTO: Producto creado.

        Raises:
            InvalidProductDataError: Si los datos proporcionados son inválidos.

        Example:
            >>> input_dto = ProductDTO(name="Mochila", ...)
            >>> creado = product_service.create_product(input_dto)
            >>> print(creado.id)
            42
        """
        try:
            product = Product(
                id=None,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e))

        saved = self.product_repository.save(product)
        return ProductDTO.model_validate(saved)

    # ------------------------------------------------------------------
    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """
        Actualiza los datos de un producto existente.

        Args:
            product_id (int): Identificador del producto a actualizar.
            product_dto (ProductDTO): Nuevos datos para el producto.

        Returns:
            ProductDTO: Producto actualizado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los datos de actualización son inválidos.

        Example:
            >>> cambios = ProductDTO(name="Nuevo Nombre", ...)
            >>> actualizado = product_service.update_product(1, cambios)
            >>> print(actualizado.name)
            'Nuevo Nombre'
        """
        existing = self.product_repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id)

        try:
            updated = Product(
                id=product_id,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as e:
            raise InvalidProductDataError(str(e))

        saved = self.product_repository.save(updated)
        return ProductDTO.model_validate(saved)

    # ------------------------------------------------------------------
    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto existente por su identificador.

        Args:
            product_id (int): Identificador del producto a eliminar.

        Returns:
            bool: True si se eliminó con éxito.

        Raises:
            ProductNotFoundError: Si el producto no existe.

        Example:
            >>> eliminado = product_service.delete_product(7)
            >>> print(eliminado)
            True
        """
        existing = self.product_repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id)

        success = self.product_repository.delete(product_id)
        return success

    # ------------------------------------------------------------------
    def get_available_products(self) -> List[ProductDTO]:
        """
        Devuelve productos que tienen stock disponible para la venta.

        Returns:
            List[ProductDTO]: Lista de productos disponibles (stock > 0).

        Example:
            >>> disponibles = product_service.get_available_products()
            >>> all(p.stock > 0 for p in disponibles)
            True
        """
        products = self.product_repository.get_all()
        available = [p for p in products if p.is_available()]
        return [ProductDTO.model_validate(p) for p in available]

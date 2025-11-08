"""Product service for database operations."""

from decimal import Decimal
from typing import List, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ecommerce.models import Deal, PriceHistory, Product
from app.utils.currency import currency_converter
from app.utils.helpers import calculate_discount_percentage, is_valid_deal


class ProductService:
    """Service for product-related database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def get_or_create_product(
        self, url: str, name: str, site: str, category: Optional[str] = None
    ) -> Product:
        """Get existing product or create new one."""
        # Check if product exists
        stmt = select(Product).where(Product.url == url)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()

        if product:
            # Update name if different
            if product.name != name:
                product.name = name
                await self.db.commit()
            return product

        # Create new product
        product = Product(name=name, url=url, site=site, category=category, is_tracked=True)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        logger.info(f"Created new product: {name} from {site}")
        return product

    async def add_price_history(
        self,
        product_id: int,
        price: Decimal,
        currency: str = "NGN",
        availability: Optional[str] = None,
    ) -> PriceHistory:
        """Add price history entry."""
        # Ensure price is in Naira
        if currency != "NGN":
            naira_price = await currency_converter.convert_to_naira(price, currency)
            price = naira_price
            currency = "NGN"

        price_entry = PriceHistory(
            product_id=product_id, price=price, currency=currency, availability=availability
        )
        self.db.add(price_entry)
        await self.db.commit()
        await self.db.refresh(price_entry)

        logger.info(f"Added price history: Product {product_id} - ₦{price}")
        return price_entry

    async def get_products_to_track(self) -> List[Product]:
        """Get all products that should be tracked."""
        stmt = select(Product).where(Product.is_tracked == True, Product.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_price(self, product_id: int) -> Optional[PriceHistory]:
        """Get latest price for a product."""
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def check_for_deal(
        self, product_id: int, current_price: Decimal, min_discount: Decimal = Decimal("5")
    ) -> Optional[Deal]:
        """Check if current price represents a deal."""
        # Get previous price
        previous_price = await self.get_latest_price(product_id)
        if not previous_price:
            return None

        # Calculate discount
        discount_percent = calculate_discount_percentage(previous_price.price, current_price)

        # Check if it's a valid deal
        if not is_valid_deal(discount_percent, min_discount):
            return None

        # Create deal entry
        deal = Deal(
            product_id=product_id,
            original_price=previous_price.price,
            deal_price=current_price,
            discount_percent=discount_percent,
            deal_type="price_drop",
        )
        self.db.add(deal)
        await self.db.commit()
        await self.db.refresh(deal)

        logger.info(f"Deal detected: Product {product_id} - {discount_percent}% off")
        return deal

    async def get_product_with_history(self, product_id: int) -> Optional[Product]:
        """Get product with price history."""
        stmt = (
            select(Product)
            .options(selectinload(Product.price_history))
            .where(Product.id == product_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

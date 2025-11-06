"""Pagination utilities for API endpoints."""

from math import ceil
from typing import Any, List, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


async def paginate_query(
    db: AsyncSession, query: Any, pagination: PaginationParams, response_model: type[T]
) -> PaginatedResponse:
    """Paginate a SQLAlchemy query and return formatted response."""

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination to query
    paginated_query = query.offset(pagination.offset).limit(pagination.size)

    # Execute query
    result = await db.execute(paginated_query)
    items = list(result.scalars().all())

    # Calculate total pages
    pages = ceil(total / pagination.size) if total > 0 else 0

    # Format items using response model
    formatted_items = [response_model.model_validate(item) for item in items]

    return PaginatedResponse(
        items=formatted_items, total=total, page=pagination.page, size=pagination.size, pages=pages
    )


async def paginate_joined_query(
    db: AsyncSession, query: Any, pagination: PaginationParams, formatter_func: callable
) -> PaginatedResponse:
    """Paginate a joined query with custom formatting function."""

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination to query
    paginated_query = query.offset(pagination.offset).limit(pagination.size)

    # Execute query
    result = await db.execute(paginated_query)
    raw_items = result.all()

    # Calculate total pages
    pages = ceil(total / pagination.size) if total > 0 else 0

    # Format items using custom formatter
    formatted_items = [formatter_func(item) for item in raw_items]

    return PaginatedResponse(
        items=formatted_items, total=total, page=pagination.page, size=pagination.size, pages=pages
    )

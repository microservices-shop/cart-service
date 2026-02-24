import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Numeric,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.db.database import Base


class CartItemModel(Base):
    __tablename__ = "cart_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    product_image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    price_changed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    out_of_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    product_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CartItemModel(id={self.id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})>"

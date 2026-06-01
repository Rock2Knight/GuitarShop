import enum
from datetime import date
from typing import TypeVar

from sqlalchemy import (
    Table, Column, Integer,
    ForeignKey, Date, CheckConstraint,
    BigInteger, Numeric, String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs

from app.database import Base, str_an, uniq_str_an

ModelClass = TypeVar('ModelClass', bound=Base)  # Generic тип для модели


class OrderStatus(str, enum.Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"


class User(Base):

    __tablename__ = "user"

    email: Mapped[uniq_str_an]
    passhash: Mapped[uniq_str_an]
    username: Mapped[uniq_str_an]

    cart: Mapped["Cart"] = relationship(
        "Cart", 
        back_populates="user", 
        uselist=False, 
        lazy="joined",
        cascade="all, delete-orphan"
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order", 
        back_populates="user",
        lazy="joined",
        cascade="save-update"
    )


class Product(Base):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    quantity: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    cart_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct", 
        back_populates="product", 
        cascade="all, delete-orphan"
    )
    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct", 
        back_populates="product", 
        cascade="all, delete-orphan"
    )


class Category(Base):
    __tablename__ = "category"

    parent_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    parent: Mapped["Category | None"] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    attributes: Mapped[list["Attributes"]] = relationship("Attributes", back_populates="category", cascade="all, delete-orphan")


class Attributes(Base):
    __tablename__ = "attributes"

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    category: Mapped["Category"] = relationship("Category", back_populates="attributes")


product_attr_values = Table(
    "product_attribute_values",
    Base.metadata,
    Column('product_id', Integer, ForeignKey('product.id', ondelete='CASCADE'), primary_key=True),
    Column('attribute_id', Integer, ForeignKey('attributes.id', ondelete='CASCADE'), primary_key=True),
    Column('value', String, nullable=False)
)


class Cart(Base):
    __tablename__ = "cart"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="cart", uselist=False, lazy="joined")

    cart_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct", 
        back_populates="cart",
        lazy="joined",
        cascade="all, delete-orphan"
    )


class Order(Base):
    __tablename__ = "order"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    status: Mapped[OrderStatus] = mapped_column(nullable=False)
    order_date: Mapped[date] = mapped_column(Date(), nullable=False)

    user: Mapped["User"] = relationship(
        "User", 
        back_populates="orders"
    )

    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct", 
        back_populates="order", 
        cascade="all, delete-orphan",
        lazy="joined"
    )


class ProductItemMixin:
    """Общие поля для позиций в корзине и заказе"""
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_time: Mapped[float] = mapped_column(Numeric(10, 2))  # замороженная цена!


class CartProduct(Base, ProductItemMixin):
    __tablename__ = "cart_product"

    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"), nullable=False)

    cart: Mapped["Cart"] = relationship(
        "Cart", 
        back_populates="cart_products"
    )


class OrderProduct(Base, ProductItemMixin):
    __tablename__ = "order_product"

    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship(
        "Order", 
        back_populates="order_products"
    )
import enum
from datetime import date

from sqlalchemy import ForeignKey, Date, CheckConstraint, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base, str_an, uniq_str_an


class ProductType(str, enum.Enum):
    GUITAR = "Guitar"
    COMBO_AMPLIFIER = "Combo Amplifier"
    PROCCESSOR = "Processor"
    EFFECT_PEDAL = "Effect Pedal"


class GuitarType(str, enum.Enum):
    ACOUSTIC = "Acoustic"
    ELECTRIC = "Electric"
    BASS = "Bass"
    BARITONE = "Baritone"


class GuitarShape(str, enum.Enum):
    CLASSIC = "Classic"
    LES_PAUL = "Les Paul"
    STRATOCASTER = "Stratocaster"
    TELECASTER = "Telecaster"
    SUPERSTRAT = "SuperStrat"
    EXPLORER = "Explorer"
    SG = "SG"
    PRS = "PRS"
    FLYING_V = "Flying V"
    MOCKINGBIRD = "Mocking Bird"
    WARLOCK = "Warlock"
    RR = "RR"
    STAR = "Star"
    ICEMAN = "Ice Man"
    FIREBIRD = "FireBird"
    JAGUAR = "Jaguar"
    MUSTANG = "Mustang"
    JAG_STANG = "Jag-Stang"


class ComboAmplifierType(str, enum.Enum):
    BULB = "Bulb"
    TRANSISTOR = "Transistor"


class OrderStatus(str, enum.Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"


class Product(Base):
    __tablename__ = "product"
    __abstract__ = True

    product_type: Mapped[ProductType] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str_an] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(CheckConstraint('quantity >= 0', name='quantity_check'), nullable=False)
    price: Mapped[float] = mapped_column(CheckConstraint('price >= 0', name='price_check'), nullable=False)


class Guitar(Product):
    __tablename__ = "guitar"

    guitar_type: Mapped[GuitarType] = mapped_column(nullable=False)
    shape: Mapped[GuitarShape] = mapped_column(nullable=True)
    fret_count: Mapped[int] = mapped_column(CheckConstraint('fret_count > 0', name='fret_count_check'), nullable=False)
    recorder_config: Mapped[str] = mapped_column(nullable=True)
    fingerboard_material: Mapped[str_an]
    body_material: Mapped[str_an]

    card_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct", 
        backref="guitar", 
        cascade="all, delete-orphan"
    )

    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="guitar",
        cascade="all, delete-orphan"
    )


class ComboAmplifier(Product):
    __tablename__ = "combo_amplifier"

    combo_type: Mapped[ComboAmplifierType] = mapped_column(nullable=False)
    effects: Mapped[str_an]
    channels_count: Mapped[int] = mapped_column(CheckConstraint('channels_count >= 0', name='channels_count_check'), nullable=False)
    power: Mapped[float] = mapped_column(nullable=True)

    card_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct",
        backref="combo",
        cascade="all, delete-orphan"
    )

    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="combo",
        cascade="all, delete-orphan"
    )

    # Добавить характеристики комбайм амплификатора


class Processor(Product):
    __tablename__ = "processor"

    express_pedal: Mapped[bool] = mapped_column(nullable=False)
    instrument_type: Mapped[str_an]
    screen_type: Mapped[str_an]

    card_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct",
        backref="processor",
        cascade="all, delete-orphan"
    )

    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="processor",
        cascade="all, delete-orphan"
    )


class EffectPedal(Product):
    __tablename__ = "effect_pedal"

    effect : Mapped[str_an]

    card_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct",
        backref="effect",
        cascade="all, delete-orphan"
    )

    order_products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="effect",
        cascade="all, delete-orphan"
    )


class User(Base):

    __tablename__ = "user"

    email: Mapped[uniq_str_an]
    passhash: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[uniq_str_an]

    cart: Mapped["Cart"] = relationship(
        "Cart", 
        back_populates="user", 
        uselist=False, 
        lazy="joined"
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order", 
        back_populates="user"
    )


class Cart(Base):
    __tablename__ = "cart"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="cart", uselist=False, lazy="joined")

    cart_products: Mapped[list["CartProduct"]] = relationship(
        "CartProduct", 
        back_populates="cart", 
        cascade="all, delete-orphan",
        lazy="joined"
    )


class CartProduct(Base):
    __tablename__ = "cart_product"

    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"), nullable=False)
    guitar_id: Mapped[int] = mapped_column(ForeignKey("guitar.id"), nullable=True)
    combo_id: Mapped[int] = mapped_column(ForeignKey("combo_amplifier.id"), nullable=True)
    processor_id: Mapped[int] = mapped_column(ForeignKey("processor.id"), nullable=True)
    effect_id: Mapped[int] = mapped_column(ForeignKey("effect_pedal.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    

    cart: Mapped["Cart"] = relationship(
        "Cart", 
        back_populates="cart_products"
    )


class OrderProduct(Base):
    __tablename__ = "order_product"

    guitar_id: Mapped[int] = mapped_column(ForeignKey("guitar.id"), nullable=True)
    combo_id: Mapped[int] = mapped_column(ForeignKey("combo_amplifier.id"), nullable=True)
    processor_id: Mapped[int] = mapped_column(ForeignKey("processor.id"), nullable=True)
    effect_id: Mapped[int] = mapped_column(ForeignKey("effect_pedal.id"), nullable=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship(
        "Order", 
        back_populates="order_products"
    )

    guitar: Mapped[Guitar] = relationship(
        "Guitar",
        back_populates="order_products"
    )

    combo: Mapped[ComboAmplifier] = relationship(
        "ComboAmplifier",
        back_populates="order_products"
    )

    processor: Mapped[Processor] = relationship(
        "Processor",
        back_populates="order_products"
    )

    effect: Mapped[EffectPedal] = relationship(
        "EffectPedal",
        back_populates="order_products"
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
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, Date, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class CategoryEnum(Enum):
    LAPTOP = "Laptop"
    PHONE = "Phone"
    TV = "TV"
    GPU = "GPU"
    CPU = "CPU"
    AC = "Air Conditioner"
    FRIDGE = "Fridge"
    FREEZERS = "Freezers"


class StoreEnum(Enum):
    ANHOCH = "Anhoch"
    DDSTORE = "DDStore"
    EKUPI = "EKupi"
    NEPTUN = "Neptun"
    SETEC = "Setec"
    TEHNOMARKET = "TehnoMarket"


class ProductCluster(Base):
    __tablename__ = "product_cluster"
    id = Column(BigInteger, primary_key=True)
    category = Column(String)

    products = relationship("Product", back_populates="product_cluster")


class Product(Base):
    __tablename__ = "product"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String)
    preprocessed_name = Column(String)
    vectorized_name = Column(JSONB)
    store = Column(String)
    link = Column(String)
    image = Column(String)
    product_cluster_id = Column(BigInteger, ForeignKey('product_cluster.id'))

    product_cluster = relationship("ProductCluster", back_populates="products")
    prices = relationship("Price")
    predictions = relationship("Prediction")


class Price(Base):
    __tablename__ = "price"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    price = Column(BigInteger)
    date = Column(Date)
    product_id = Column(BigInteger, ForeignKey('product.id'))

    product = relationship("Product", back_populates="prices")


class Prediction(Base):
    __tablename__ = 'prediction'
    id = Column(BigInteger, primary_key=True)
    prediction_result = Column(String)
    prediction_accuracy = Column(Boolean)
    predicted_on = Column(Date)
    previous_price = Column(BigInteger)
    next_predicted_price = Column(BigInteger)
    product_id = Column(BigInteger, ForeignKey('product.id'))

    product = relationship("Product", back_populates="predictions")

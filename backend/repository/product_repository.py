from sqlalchemy import Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from models.models import Product, PastPrice
from repository.database import Session


def get_current_price_for_product_by_id(product_id: Integer):
    session = None
    try:
        session = Session()
        product = session.query(Product).filter(Product.id == product_id).options(
            joinedload(Product.current_price)).first()
        return product.current_price
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_past_prices_for_product_by_id(product_id: Integer):
    session = None
    try:
        session = Session()
        past_prices = session.query(PastPrice).filter(PastPrice.product_id == product_id).all()
        return past_prices
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_all_products():
    session = None
    try:
        session = Session()
        all_products = session.query(Product).options(joinedload(Product.current_price)).all()
        for p in all_products:
            if p.product_cluster:
                p.category = p.product_cluster.category
                session.commit()
        return all_products
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_all_products_from_category(category: str):
    session = None
    try:
        session = Session()
        products = session.query(Product).filter(Product.category == category).all()
        return products
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def update_cluster_for_product(link, cluster_id):
    session = None
    try:
        session = Session()
        product = session.query(Product).filter(Product.link == link).first()
        product.product_cluster_id=cluster_id
        session.commit()
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_training_data():
    session = None
    try:
        session = Session()
        products = session.query(Product).all()
        return products
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()

from sqlalchemy import Integer, String, Date
from sqlalchemy.orm import joinedload

from models.models import Product, PastPrice, CurrentPrice, ProductCluster
from repository.database import Session
from sqlalchemy.exc import SQLAlchemyError


def get_product_by_link_or_name(link: String):
    session = None
    try:
        session = Session()
        product = session.query(Product).filter(Product.link == link).options(joinedload(Product.current_price)).first()
        return product
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def add_new_price_to_product(link: String, new_price: Integer, date: Date):
    session = None
    try:
        session = Session()
        product = session.query(Product).filter(Product.link == link).first()
        past_price = PastPrice(price=product.current_price.price, date=product.current_price.date,
                               product_id=product.id)
        session.add(past_price)
        product.current_price.price = new_price
        product.current_price.date = date
        session.commit()
        return product
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def add_new_product(name, link, image, regular_price, category, store, date, preprocessed_name):
    session = None
    try:
        session = Session()
        current_price = CurrentPrice(price=regular_price, date=date)
        session.add(current_price)
        session.commit()
        product = Product(name=name, link=link, image=image, category=category, store=store,
                          current_price_id=current_price.id, preprocessed_name=preprocessed_name)
        session.add(product)
        session.commit()
        return product
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def remove_all_clusters():
    session = None
    try:
        session = Session()
        session.query(ProductCluster).delete()
        session.commit()
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def create_new_cluster(cluster_id, category):
    session = None
    try:
        session = Session()
        product_cluster = ProductCluster(id=cluster_id, category=category)
        session.add(product_cluster)
        session.commit()
        return product_cluster
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def update_image(link: String, image: String):
    session = None
    try:
        session = Session()
        product = session.query(Product).filter(Product.link == link).first()
        product.image = image
        session.commit()
        return product
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()

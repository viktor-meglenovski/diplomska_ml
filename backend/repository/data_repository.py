from datetime import date

from sqlalchemy import Integer, String, Date, desc, func, bindparam
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy import text

from models.models import Product, PastPrice, CurrentPrice, ProductCluster, ScrapingDate, Prediction
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


def get_latest_scraping_dates(num):
    session = None
    try:
        session = Session()
        dates = session.query(ScrapingDate).order_by(desc(ScrapingDate.date)).limit(num).all()
        dates = [str(date.date) for date in dates]
        dates.reverse()
        return dates
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_dataset(dates):
    session = None
    try:
        session = Session()
        dates_param = str(dates).replace('[', '(').replace(']', ')')
        sql_query1 = text(f"""
            SELECT p.id, p.category, p.store, pp.price, pp.date
            FROM product p
            JOIN past_price pp ON p.id = pp.product_id AND pp.date IN {dates_param}
        """)
        sql_query2 = text(f"""
            SELECT p.id, p.category, p.store, cp.price, cp.date
            FROM product p
            JOIN current_price cp ON p.current_price_id = cp.id AND cp.date IN {dates_param}
        """)

        result1 = session.execute(sql_query1)
        result2 = session.execute(sql_query2)
        rows1 = result1.fetchall()
        rows2 = result2.fetchall()
        rows = list()
        for r in rows1:
            rows.append(r)
        for r in rows2:
            rows.append(r)
        return rows
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def evaluate_previous_prediction(product_id, price, prediction_date):
    session = None
    try:
        session = Session()
        prediction = (session.query(Prediction)
                      .filter(Prediction.product_id == product_id)
                      .filter(Prediction.predicted_on == prediction_date)
                      .first())
        if not prediction:
            return
        threshold = prediction.previous_price*0.05
        prediction.next_actual_price = price
        prediction.prediction_accuracy = abs(price-prediction.prediction_result) < threshold
        session.commit()
        return prediction
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def add_new_scraping_date(date_to_add):
    session = None
    try:
        session = Session()
        scraping_date = ScrapingDate(date=date_to_add)
        session.add(scraping_date)
        session.commit()
        return scraping_date
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()

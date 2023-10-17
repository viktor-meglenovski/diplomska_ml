from datetime import date

from sqlalchemy import Integer, String, Date, desc, func, bindparam
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy import text

from models.models import Product, PastPrice, CurrentPrice, ProductCluster, ScrapingDate, Prediction, MLModel
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


def get_all_scraping_dates():
    session = None
    try:
        session = Session()
        dates = session.query(ScrapingDate).order_by(desc(ScrapingDate.date)).all()
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


def evaluate_previous_prediction(product_id, price, prediction_date, evaluated_on):
    session = None
    try:
        session = Session()
        prediction = (session.query(Prediction)
                      .filter(Prediction.product_id == product_id)
                      .filter(Prediction.predicted_on == prediction_date)
                      .filter(Prediction.is_passed == False)
                      .first())
        if not prediction:
            return
        threshold = prediction.previous_price*0.05
        prediction.next_actual_price = price
        prediction.prediction_accuracy = abs(price-prediction.next_predicted_price) < threshold
        prediction.evaluated_on = evaluated_on
        session.commit()
        return 1 if prediction.prediction_accuracy else 0
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


def add_new_ml_model(model_name, created_on, testing_accuracy):
    session = None
    try:
        session = Session()
        ml_model = MLModel(model_name=model_name, created_on=created_on, testing_accuracy=testing_accuracy)
        session.add(ml_model)
        session.commit()
        return ml_model
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def update_latest_ml_model(correct_predictions, all_predictions):
    session = None
    try:
        session = Session()
        ml_model = session.query(MLModel).filter(MLModel.actual_accuracy == None).first()
        if not ml_model:
            return
        ml_model.actual_accuracy = correct_predictions / all_predictions * 100
        session.commit()
        return ml_model
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_all_evaluated_ml_models():
    session = None
    try:
        session = Session()
        ml_models = session.query(MLModel).filter(MLModel.actual_accuracy == None).all()
        return ml_models
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def add_new_prediction(predicted_on, next_predicted_price, predicted_percentage_result, prediction_result, previous_price, product_id):
    session = None
    try:
        session = Session()
        prediction = Prediction(predicted_on=predicted_on, next_predicted_price=next_predicted_price, predicted_percentage=predicted_percentage_result, prediction_result=prediction_result, previous_price=previous_price, product_id=product_id, is_passed=False)
        session.add(prediction)
        session.commit()
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def mark_all_predictions_as_passed():
    session = None
    try:
        session = Session()
        predictions = session.query(Prediction).filter(Prediction.is_passed == False).all()
        for p in predictions:
            p.is_passed = True
            session.commit()
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_all_ml_models():
    session = None
    try:
        session = Session()
        models = session.query(MLModel).order_by(MLModel.created_on).all()
        return models
    except SQLAlchemyError as e:
        if session:
            session.rollback()
        raise e
    finally:
        if session:
            session.close()


def get_research_dataset(dates):
    session = None
    try:
        session = Session()
        dates_param = str(dates).replace('[', '(').replace(']', ')')
        sql_query1 = text(f"""
            SELECT p.id, p.name, p.link, p.category, p.store,  p.product_cluster_id, pp.price, pp.date
            FROM product p
            JOIN past_price pp ON p.id = pp.product_id AND pp.date IN {dates_param}
        """)
        sql_query2 = text(f"""
            SELECT p.id,  p.name, p.link,  p.category, p.store,  p.product_cluster_id, cp.price, cp.date
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

from models.models import ProductCluster, Product, PastPrice, CurrentPrice
from repository.database import Session
import pandas as pd


# def populate_products():
#     session = Session()
#     products = pd.read_csv("helpers\\data_scraping\\data\\initial_data_preprocessed.csv")
#     grouped = products.groupby('cluster_id')
#     product_id = 1
#     past_price_id = 1
#     current_price_id = 1
#     for cluster_id, cluster in grouped:
#         cluster_category = cluster.values[0][3]
#         new_product_cluster = ProductCluster(id=cluster_id+1, category=cluster_category)
#         session.add(new_product_cluster)
#         session.commit()
#         for product in cluster.values:
#             first_price_index = 9
#             number_of_prices = 3
#             new_product = Product(id=product_id, product_cluster_id=cluster_id+1, image=product[2], link=product[1],
#                                   name=product[0],
#                                   preprocessed_name=product[5], store=product[4], vectorized_name=product[8])
#             session.add(new_product)
#             session.commit()
#
#             # Add Past Prices
#             for i in range(number_of_prices - 1):
#                 column = cluster.columns[first_price_index + i]
#                 past_price = PastPrice(id=past_price_id, price=product[first_price_index + i], date=column,
#                                        product_id=new_product.id)
#                 session.add(past_price)
#                 session.commit()
#                 past_price_id += 1
#
#             # Add Current Price
#             column = cluster.columns[first_price_index + i]
#             current_price = CurrentPrice(id=current_price_id, price=product[first_price_index + i], date=column)
#             session.add(current_price)
#             session.commit()
#             new_product.current_price_id = current_price.id
#             session.commit()
#             current_price_id += 1
#
#             product_id += 1
#     session.close()

def populate_products():
    session = Session()
    products = pd.read_csv("helpers\\data_scraping\\data\\initial_data_preprocessed.csv")
    grouped = products.groupby('cluster_id')
    for cluster_id, cluster in grouped:
        cluster_category = cluster.values[0][3]
        new_product_cluster = ProductCluster(category=cluster_category)
        session.add(new_product_cluster)
        session.commit()
        for product in cluster.values:
            first_price_index = 9
            number_of_prices = 3
            new_product = Product(product_cluster_id=new_product_cluster.id, image=product[2],
                                  link=product[1],
                                  name=product[0],
                                  preprocessed_name=product[5], store=product[4], category=product[3], vectorized_name=product[8])
            session.add(new_product)
            session.commit()

            # Add Past Prices
            for i in range(number_of_prices - 1):
                column = cluster.columns[first_price_index + i]
                past_price = PastPrice(price=product[first_price_index + i], date=column,
                                       product_id=new_product.id)
                session.add(past_price)
                session.commit()

            # Add Current Price
            column = cluster.columns[first_price_index + i]
            current_price = CurrentPrice(price=product[first_price_index + i], date=column)
            session.add(current_price)
            session.commit()
            new_product.current_price_id = current_price.id
            session.commit()

    session.close()

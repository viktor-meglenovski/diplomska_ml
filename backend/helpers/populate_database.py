from models.Models import ProductCluster, Product, Price
from repository.database import Session
import pandas as pd


def populate_products():
    session = Session()
    products = pd.read_csv("helpers\\data_scraping\\data\\initial_data_preprocessed.csv")
    grouped = products.groupby('cluster_id')
    product_id = 0
    price_id = 0
    for cluster_id, cluster in grouped:
        cluster_category = cluster.values[0][3]
        new_product_cluster = ProductCluster(id=cluster_id, category=cluster_category)
        session.add(new_product_cluster)
        session.commit()
        for product in cluster.values:
            new_product = Product(id=product_id, product_cluster_id=cluster_id, image=product[2], link=product[1],
                                  name=product[0],
                                  preprocessed_name=product[5], store=product[4], vectorized_name=product[8])
            session.add(new_product)
            session.commit()
            product_id += 1
            first_price_index = 9
            number_of_prices = 3
            for i in range(number_of_prices):
                column = cluster.columns[first_price_index + i]
                new_price = Price(id=price_id, date=column, price=product[first_price_index + i],
                                  product_id=new_product.id)
                session.add(new_price)
                session.commit()
                price_id += 1
    session.close()

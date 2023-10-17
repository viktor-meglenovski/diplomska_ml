import string

import pandas as pd

import repository.data_repository as data_repository
import repository.product_repository as product_repository
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.cluster import AgglomerativeClustering

from service.training_service import train_model_and_make_predictions


def add_new_data(file):
    scraped_data = pd.read_csv(file)
    date = scraped_data['date'][0]
    new_products = 0
    existing_products = 0
    correct_predictions = 0
    all_predictions = 0
    for row in scraped_data.values:
        link = row[1].lower()
        link = f"https://www.ekupi.mk{link}" if row[5] == "EKupi" else link
        preprocessed_name = _preprocess_name(row[0])
        existing_product = data_repository.get_product_by_link_or_name(link)
        if existing_product:
            data_repository.update_image(existing_product.link, row[2])
            if str(existing_product.current_price.date) != date:
                is_correct = data_repository.evaluate_previous_prediction(existing_product.id, row[3],
                                                             existing_product.current_price.date, date)
                if is_correct:
                    correct_predictions+=is_correct
                all_predictions += 1
                data_repository.add_new_price_to_product(existing_product.link, row[3], date)
                existing_products += 1
        else:
            data_repository.add_new_product(row[0], link, row[2], row[3], row[4], row[5], row[6], preprocessed_name)
            new_products += 1
    cluster_products()
    data_repository.add_new_scraping_date(date)
    data_repository.update_latest_ml_model(correct_predictions, all_predictions)
    data_repository.mark_all_predictions_as_passed()
    train_model_and_make_predictions(5)

    return existing_products, new_products


def _preprocess_name(text):
    text = text.lower()
    text = text.replace('\\', ' ').replace('/', ' ')
    text = ''.join([char for char in text if char not in string.punctuation])
    return text


def cluster_products():
    data_repository.remove_all_clusters()
    categories = ['LAPTOP', 'TV', 'PHONE', 'CPU', 'GPU', 'AC', 'FRIDGE', 'FREEZER']
    for category in categories:
        _cluster_products_from_category(category)


def _cluster_products_from_category(category: str):
    # Get all products from the given category
    all_products_from_category = product_repository.get_all_products_from_category(category)

    # Build a DataFrame out of products
    df = _build_df_from_products(all_products_from_category)

    # Do the clustering
    df = _cluster_dataframe(df, category)

    # Group the DataFrame by cluster ID
    groups = df.groupby(by='cluster')

    # For each group create the cluster
    for group_key, group_df in groups:
        data_repository.create_new_cluster(group_key, category)

        # For each item in that group update their cluster ID
        for index, row in group_df.iterrows():
            product_repository.update_cluster_for_product(row['link'], row['cluster'])


def _build_df_from_products(products):
    rows = list()
    for product in products:
        row = dict()
        row['link'] = product.link
        row['preprocessed_name'] = product.preprocessed_name
        rows.append(row)
    df = pd.DataFrame(rows)
    return df


def _cluster_dataframe(df, category):
    product_names = df['preprocessed_name'].tolist()
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(product_names)
    dense_tfidf_matrix = tfidf_matrix.toarray()
    jaccard_distance = pairwise_distances(dense_tfidf_matrix, metric='jaccard')
    agg_clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.05)
    cluster_labels = agg_clustering.fit_predict(jaccard_distance)
    df['cluster'] = cluster_labels
    df['cluster'] = df.apply(lambda row: f"{category}{row['cluster']}", axis=1)
    return df




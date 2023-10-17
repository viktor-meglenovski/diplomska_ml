import pickle
from datetime import date

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import repository.data_repository as data_repository

with open('helpers\\encoders\\category_encoder.pkl', 'rb') as file:
    category_encoder = pickle.load(file)

with open('helpers\\encoders\\store_encoder.pkl', 'rb') as file:
    store_encoder = pickle.load(file)


def train_model_and_make_predictions(number_of_prices=5):
    df, csv_content, file_name, dates, rows = create_training_df(number_of_prices)
    encoded_df = _encode_training_df(df, number_of_prices)
    train_data, test_data, validation_data, X_train, y_train, X_test, y_test, X_validation, y_validation, accuracy_test = _split_dataset(
        encoded_df)
    model = _train_model(train_data, test_data, validation_data, X_train, y_train, X_test, y_test, X_validation,
                         y_validation,
                         accuracy_test, number_of_prices)

    new_predictions_df = create_predictions_df(number_of_prices - 1)
    new_predictions_df_encoded = _encode_dataset_for_making_predictions(new_predictions_df, number_of_prices - 1)
    new_predictions = model.predict(new_predictions_df_encoded.iloc[:, :-1]).astype(int)

    new_predictions_df_encoded['predicted_price'] = new_predictions
    new_predictions_df_encoded['predicted_difference'] = new_predictions_df_encoded['predicted_price'] - \
                                                         new_predictions_df_encoded[f'price{number_of_prices - 1}']
    new_predictions_df_encoded['predicted_output'] = new_predictions_df_encoded['predicted_difference'] / \
                                                     new_predictions_df_encoded[f'price{number_of_prices - 1}']
    new_predictions_df_encoded['predicted_output_label'] = new_predictions_df_encoded['predicted_output'].apply(
        lambda x: 'UP' if x >= 0.05 else 'DOWN' if x <= -0.05 else 'SAME')
    new_predictions_df_encoded = new_predictions_df_encoded[
        ['id', f'price{number_of_prices - 1}', 'predicted_price', 'predicted_difference', 'predicted_output',
         'predicted_output_label']]

    today = date.today()
    for row in new_predictions_df_encoded.values:
        product_id = row[0]
        previous_price = row[1]
        next_predicted_price = row[2]
        predicted_percentage = row[4]
        prediction_result = row[5]
        data_repository.add_new_prediction(today, next_predicted_price, predicted_percentage, prediction_result,
                                           previous_price, product_id)


def create_training_df(number_of_prices):
    dates = data_repository.get_latest_scraping_dates(number_of_prices)
    if len(dates) < number_of_prices:
        raise Exception
    rows = data_repository.get_dataset(dates)
    df = pd.DataFrame(rows)
    df['date']=df['date'].astype(str)
    pivot_df = df.pivot(index=['id', 'category', 'store'], columns='date', values='price').reset_index()
    pivot_df=pivot_df.dropna()
    today = date.today()
    training_dataset_path = f"helpers\\training_datasets\\training_dataset_{today}.csv"
    pivot_df.to_csv(training_dataset_path, index=False)
    csv_content = pivot_df.to_csv(index=False)

    return pivot_df, csv_content, f"training_dataset_{today}.csv", dates, pivot_df.shape[0]


def create_research_training_df():
    dates = data_repository.get_all_scraping_dates()
    rows = data_repository.get_research_dataset(dates)
    df = pd.DataFrame(rows)
    df['date']=df['date'].astype(str)
    pivot_df = df.pivot(index=['id','name', 'link', 'category', 'store', 'product_cluster_id'], columns='date', values='price').reset_index()
    today = date.today()
    training_dataset_path = f"helpers\\training_datasets\\research_dataset_{today}.csv"
    pivot_df.to_csv(training_dataset_path, index=False)
    csv_content = pivot_df.to_csv(index=False)

    return pivot_df, csv_content, f"research_dataset_{today}.csv", dates, pivot_df.shape[0]


def create_predictions_df(number_of_prices):
    dates = data_repository.get_latest_scraping_dates(number_of_prices)
    rows = data_repository.get_dataset(dates)
    df = pd.DataFrame(rows)
    pivot_df = df.pivot(index=['id', 'category', 'store'], columns='date', values='price').reset_index()
    pivot_df.dropna(inplace=True)

    return pivot_df


def _encode_training_df(df_original, number_of_prices):
    df = df_original.copy()
    df.drop(columns=['id'], inplace=True)
    df = df.reset_index(drop=True)
    category_encoded = category_encoder.transform(df[['category']]).astype(int)
    store_encoded = store_encoder.transform(df[['store']]).astype(int)
    category_encoded_df = pd.DataFrame(category_encoded, columns=category_encoder.get_feature_names_out(['category']))
    store_encoded_df = pd.DataFrame(store_encoded, columns=store_encoder.get_feature_names_out(['store']))
    category_encoded_df = category_encoded_df.reset_index(drop=True)
    store_encoded_df = store_encoded_df.reset_index(drop=True)
    df_encoded = pd.concat([df, category_encoded_df, store_encoded_df], axis=1)
    df_encoded = df_encoded.drop(['category', 'store'], axis=1)

    price_columns = df_encoded.columns[0:number_of_prices]
    for price in price_columns:
        df_encoded[price] = df_encoded[price].astype(int)
    new_price_columns = dict()
    for i, price in enumerate(price_columns):
        if i == number_of_prices - 1:
            new_price_columns[price] = f"target"
        else:
            new_price_columns[price] = f"price{i + 1}"

    df_encoded.rename(columns=new_price_columns, inplace=True)
    columns = df_encoded.columns
    desired_order = columns[number_of_prices:].tolist() + columns[0:number_of_prices - 1].tolist() + [
        columns[number_of_prices - 1]]
    df_encoded = df_encoded[desired_order]
    df_encoded['difference'] = df_encoded['target'] - df_encoded[f'price{number_of_prices - 1}']
    df_encoded['output'] = df_encoded['difference'] / df_encoded[f'price{number_of_prices - 1}']
    df_encoded['output_label'] = df_encoded['output'].apply(
        lambda x: 'UP' if x >= 0.05 else 'DOWN' if x <= -0.05 else 'SAME')

    return df_encoded


def _encode_dataset_for_making_predictions(df_original, number_of_prices):
    df = df_original.copy()
    df = df.reset_index(drop=True)
    category_encoded = category_encoder.transform(df[['category']]).astype(int)
    store_encoded = store_encoder.transform(df[['store']]).astype(int)
    category_encoded_df = pd.DataFrame(category_encoded, columns=category_encoder.get_feature_names_out(['category']))
    store_encoded_df = pd.DataFrame(store_encoded, columns=store_encoder.get_feature_names_out(['store']))
    category_encoded_df = category_encoded_df.reset_index(drop=True)
    store_encoded_df = store_encoded_df.reset_index(drop=True)
    df_encoded = pd.concat([df, category_encoded_df, store_encoded_df], axis=1)
    df_encoded = df_encoded.drop(['category', 'store'], axis=1)

    price_columns = df_encoded.columns[1:number_of_prices + 1]
    for price in price_columns:
        df_encoded[price] = df_encoded[price].astype(int)
    new_price_columns = dict()
    for i, price in enumerate(price_columns):
        new_price_columns[price] = f"price{i + 1}"

    df_encoded.rename(columns=new_price_columns, inplace=True)
    columns = df_encoded.columns
    print(columns)
    desired_order = columns[number_of_prices + 1:].tolist() + columns[1:number_of_prices + 1].tolist() + [
        columns[0]]
    df_encoded = df_encoded[desired_order]

    return df_encoded


def _split_dataset(df_encoded):
    df = df_encoded.copy()
    train_data, test_validation_data = train_test_split(df, test_size=0.4, shuffle=True)
    test_data, validation_data = train_test_split(test_validation_data, test_size=0.5, shuffle=True)

    x = df_encoded.columns[0:-4]
    y = [df_encoded.columns[-4]]

    X_train = train_data[x]
    y_train = train_data[y]
    X_test = test_data[x]
    y_test = test_data[y]
    X_validation = validation_data[x]
    y_validation = validation_data[y]
    accuracy_test = validation_data[['output_label']]

    return train_data, test_data, validation_data, X_train, y_train, X_test, y_test, X_validation, y_validation, accuracy_test


def _train_model(train_data, test_data, validation_data, X_train, y_train, X_test, y_test, X_validation, y_validation,
                 accuracy_test, number_of_prices):
    X_train_combined = pd.concat([X_train, X_validation], axis=0)
    y_train_combined = np.concatenate([y_train, y_validation])
    model = RandomForestRegressor()
    model.fit(X_train_combined, y_train_combined)
    predictions = model.predict(X_test)
    predictions_df = _process_prediction_output_pseudo(predictions, y_test, test_data, number_of_prices)
    all_rows = predictions_df.shape[0]
    correct_rows = predictions_df[predictions_df['output_label'] == predictions_df['predicted_output_label']].shape[0]
    model_accuracy = correct_rows / all_rows * 100

    data_repository.add_new_ml_model("Random Forest Regressor", date.today(), model_accuracy)
    return model


def _process_prediction_output_pseudo(predictions, y_test, test_data, number_of_prices):
    predictions_df = pd.DataFrame(predictions, columns=['predicted_target'])
    predictions_df['predicted_target'] = predictions_df['predicted_target'].astype(int)
    evaluation_validation = test_data[
        ['target', 'output_label', f'price{number_of_prices - 1}', 'output', 'difference']]
    evaluation_validation.reset_index(drop=True, inplace=True)
    predictions_df = pd.concat([predictions_df, evaluation_validation], axis=1)
    predictions_df['predicted_difference'] = predictions_df['predicted_target'] - predictions_df[
        f'price{number_of_prices - 1}']
    predictions_df['predicted_output'] = predictions_df['predicted_difference'] / predictions_df[
        f'price{number_of_prices - 1}']
    predictions_df['predicted_output_label'] = predictions_df['predicted_output'].apply(
        lambda x: 'UP' if x >= 0.05 else 'DOWN' if x <= -0.05 else 'SAME')
    return predictions_df

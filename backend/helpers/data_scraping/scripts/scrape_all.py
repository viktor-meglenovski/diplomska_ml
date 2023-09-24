import shutil

import pandas as pd
import os
from datetime import date
import csv
import io

from helpers.data_scraping.scripts.Anhoch_Scraping import scrape_data as anhoch
from helpers.data_scraping.scripts.DDStore_Scraping import scrape_data as ddstore
from helpers.data_scraping.scripts.EKupi_Scraping import scrape_data as ekupi
from helpers.data_scraping.scripts.Neptun_Scraping import scrape_data as neptun
from helpers.data_scraping.scripts.Setec_Scraping import scrape_data as setec
from helpers.data_scraping.scripts.TehnoMarket_Scraping import scrape_data as tehnomarket


def scrape_all():
    today = date.today()
    data_path = f"helpers\\data_scraping\\data"
    today_data_path = f"{data_path}\\{today}"
    if os.path.exists(today_data_path):
        shutil.rmtree(today_data_path)
    os.makedirs(today_data_path)

    file_list = []
    all_stats = {}

    file_name, stats = anhoch(today_data_path)
    file_list.append(file_name)
    all_stats['Anhoch'] = stats

    file_name, stats = ddstore(today_data_path)
    file_list.append(file_name)
    all_stats['DDStore'] = stats

    file_name, stats = ekupi(today_data_path)
    file_list.append(file_name)
    all_stats['EKupi'] = stats

    file_name, stats = neptun(today_data_path)
    file_list.append(file_name)
    all_stats['Neptun'] = stats

    file_name, stats = setec(today_data_path)
    file_list.append(file_name)
    all_stats['Setec'] = stats

    file_name, stats = tehnomarket(today_data_path)
    file_list.append(file_name)
    all_stats['TehnoMarket'] = stats

    dfs = []
    for file in file_list:
        df = pd.read_csv(file)
        columns_to_check = set(df.columns)
        if 'discount_price' not in columns_to_check:
            df['discount_price'] = None
        dfs.append(df)
    result_df = pd.concat(dfs, axis=0)

    file_name = f'{data_path}\\all_data_{date.today()}.csv'

    if os.path.exists(file_name):
        os.remove(file_name)

    result_df.to_csv(file_name, index=False)
    csv_content = result_df.to_csv(index=False)

    total_number = result_df.shape[0]

    return csv_content, file_name, all_stats, total_number

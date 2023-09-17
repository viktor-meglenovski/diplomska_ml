import pandas as pd
import os
from datetime import date

from helpers.data_scraping.scripts.Anhoch_Scraping import scrape_data as anhoch
from helpers.data_scraping.scripts.DDStore_Scraping import scrape_data as ddstore
from helpers.data_scraping.scripts.EKupi_Scraping import scrape_data as ekupi
from helpers.data_scraping.scripts.Neptun_Scraping import scrape_data as neptun
from helpers.data_scraping.scripts.Setec_Scraping import scrape_data as setec
from helpers.data_scraping.scripts.TehnoMarket_Scraping import scrape_data as tehnomarket

def scrape_all():
    today=date.today()
    data_path = f"helpers\\data_scraping\\data"
    today_data_path = f"{data_path}\\{today}"
    if not os.path.exists(today_data_path):
        os.makedirs(today_data_path)

    # call all scraping functions
    # anhoch(today_data_path)
    ddstore(today_data_path)
    ekupi(today_data_path)
    neptun(today_data_path)
    setec(today_data_path)
    tehnomarket(today_data_path)

    file_list = os.listdir(today_data_path)
    dfs = []
    for file in file_list:
        df = pd.read_csv(f"{today_data_path}\{file}")
        columns_to_check = set(df.columns)
        if 'discount_price' not in columns_to_check:
            df['discount_price'] = None
        dfs.append(df)
    result_df = pd.concat(dfs, axis=0)
    result_df.to_csv(f'{data_path}\\all_data_{date.today()}.csv', index=False)
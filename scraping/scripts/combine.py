import pandas as pd
import os
from datetime import date


directory_path = r'C:\Users\Viktor\Desktop\Diplomska Scraping\data\2023-08-24'
file_list = os.listdir(directory_path)

dfs = []
for file in file_list:
    df = pd.read_excel(f"{directory_path}\{file}")
    columns_to_check = set(df.columns)
    if 'discount_price' not in columns_to_check:
        df['discount_price'] = None
    dfs.append(df)
result_df = pd.concat(dfs, axis=0)
result_df.drop(columns=['code'], inplace=True)
result_df.to_excel(f'all_data_{date.today()}.xlsx', index=False)
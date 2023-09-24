from selenium import webdriver
import time
from datetime import date
from selenium.webdriver.common.by import By
import pandas as pd


def load_products(stats, driver, all_products, base_url, category, price_lower_bound_threshold=1000):
    page = 1
    while True:
        driver.get(f"{base_url}{page}")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        products = driver.find_elements(By.CSS_SELECTOR, "div.ng-scope.product-list-item-grid")
        for p in products:
            product_row = dict()
            name_element = p.find_element(By.CSS_SELECTOR, "div.white-box > a")
            product_row['name'] = name_element.find_element(By.CSS_SELECTOR,
                                                            "h2.product-list-item__content--title").text

            product_row['link'] = name_element.get_attribute('href')

            product_row['image'] = p.find_element(By.CSS_SELECTOR, "img.ng-scope").get_attribute('src')

            regular_price = p.find_element(By.CSS_SELECTOR, "div.Regular")
            regular_price = regular_price.find_elements(By.CSS_SELECTOR, "span.product-price__amount--value")
            regular_price = regular_price[0].text
            product_row['regular_price'] = int(regular_price.replace('.', ''))
            if product_row['regular_price'] < price_lower_bound_threshold:
                continue

            discount_price = None
            discount_price = p.find_element(By.CSS_SELECTOR, "div.HappyCard")
            discount_price = discount_price.find_elements(By.CSS_SELECTOR, "span.product-price__amount--value")
            if len(discount_price) > 0:
                discount_price = discount_price[0].text
                product_row['discount_price'] = int(discount_price.replace('.', ''))
            else:
                product_row['discount_price'] = None

            product_row['category'] = category
            all_products.append(product_row)
            stats[category] += 1
        if len(products) < 100:
            break
        page += 1


def scrape_data(folder_path):
    driver = webdriver.Firefox()
    all_products = list()
    stats = {
        'LAPTOP': 0,
        'PHONE': 0,
        'TV': 0,
        'GPU': 0,
        'CPU': 0,
        'AC': 0,
        'FRIDGE': 0,
        'FREEZER': 0
    }
    load_products(stats, driver, all_products, 'https://www.neptun.mk/prenosni_kompjuteri.nspx?items=100&page=',
                  'LAPTOP')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/mobilni_telefoni.nspx?items=100&page=', 'PHONE',
                  price_lower_bound_threshold=3000)
    load_products(stats, driver, all_products, 'https://www.neptun.mk/televizori.nspx?items=100&page=', 'TV')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/Procesori.nspx?items=100&page=', 'CPU')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/INVERTER_SISTEMI.nspx?items=100&page=', 'AC')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/SPLIT_SISTEMI.nspx?items=100&page=', 'AC')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/FRIZIDERI1.nspx?items=100&page=', 'FRIDGE')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/KOMBINIRANI_FRIZIDERI.nspx?items=100&page=',
                  'FRIDGE')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/SIDE_BY_SIDE_FRIZIDERI.nspx?items=100&page=',
                  'FRIDGE')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/HORIZONTALNI.nspx?items=100&page=', 'FREEZER')
    load_products(stats, driver, all_products, 'https://www.neptun.mk/VERTIKALNI.nspx?items=100&page=', 'FREEZER')
    # NO GPUs AVAILABLE ON NEPTUN

    df = pd.DataFrame.from_dict(all_products)
    df['store'] = 'Neptun'
    df['date'] = date.today()
    file_name = f"{folder_path}\\neptun_{date.today()}.csv"
    df.to_csv(file_name, index=False)
    driver.quit()
    return file_name, stats

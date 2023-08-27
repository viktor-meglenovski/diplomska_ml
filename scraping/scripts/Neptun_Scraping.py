from selenium import webdriver
import time
from datetime import date
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Firefox()


def load_products(all_products, base_url, category, price_lower_bound_threshold=1000):
    page=1
    while True:
        driver.get(f"{base_url}{page}")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        products = driver.find_elements(By.CSS_SELECTOR, "div.ng-scope.product-list-item-grid")  
        for p in products:
            product_row=dict()
            name_element=p.find_element(By.CSS_SELECTOR, "div.white-box > a")
            product_row['name']=name_element.find_element(By.CSS_SELECTOR, "h2.product-list-item__content--title").text

            product_row['link']=name_element.get_attribute('href')

            product_row['image']=p.find_element(By.CSS_SELECTOR, "img.ng-scope").get_attribute('src')

            regular_price=p.find_element(By.CSS_SELECTOR, "div.Regular")
            regular_price=regular_price.find_elements(By.CSS_SELECTOR, "span.product-price__amount--value")
            regular_price=regular_price[0].text
            product_row['regular_price']=int(regular_price.replace('.',''))
            if product_row['regular_price'] < price_lower_bound_threshold:
                continue

            discount_price=None
            discount_price=p.find_element(By.CSS_SELECTOR, "div.HappyCard")
            discount_price=discount_price.find_elements(By.CSS_SELECTOR, "span.product-price__amount--value")
            if len(discount_price) > 0:
                discount_price=discount_price[0].text
                product_row['discount_price']=int(discount_price.replace('.',''))
            else:
                product_row['discount_price']=None

            product_row['category']=category
            all_products.append(product_row)
        if len(products)<100:
            break  
        page+=1

def scrape_data():
    all_products=list()
    load_products(all_products, 'https://www.neptun.mk/prenosni_kompjuteri.nspx?items=100&page=', 'Laptop')
    load_products(all_products, 'https://www.neptun.mk/mobilni_telefoni.nspx?items=100&page=', 'Phone', price_lower_bound_threshold=3000)
    load_products(all_products, 'https://www.neptun.mk/televizori.nspx?items=100&page=', 'TV')
    load_products(all_products, 'https://www.neptun.mk/Procesori.nspx?items=100&page=', 'CPU')
    load_products(all_products, 'https://www.neptun.mk/INVERTER_SISTEMI.nspx?items=100&page=', 'Air Conditioner')
    load_products(all_products, 'https://www.neptun.mk/SPLIT_SISTEMI.nspx?items=100&page=', 'Air Conditioner')
    load_products(all_products, 'https://www.neptun.mk/FRIZIDERI1.nspx?items=100&page=', 'Fridge')
    load_products(all_products, 'https://www.neptun.mk/KOMBINIRANI_FRIZIDERI.nspx?items=100&page=', 'Fridge')
    load_products(all_products, 'https://www.neptun.mk/SIDE_BY_SIDE_FRIZIDERI.nspx?items=100&page=', 'Fridge')
    load_products(all_products, 'https://www.neptun.mk/HORIZONTALNI.nspx?items=100&page=', 'Freezers')
    load_products(all_products, 'https://www.neptun.mk/VERTIKALNI.nspx?items=100&page=', 'Freezers')
    # NO GPUs AVAILABLE ON NEPTUN

    df=pd.DataFrame.from_dict(all_products)
    df['store']='Neptun'
    df['date']= date.today()
    print(df)
    df.to_excel(f"neptun_{date.today()}.xlsx", index=False)
    driver.quit()

scrape_data()
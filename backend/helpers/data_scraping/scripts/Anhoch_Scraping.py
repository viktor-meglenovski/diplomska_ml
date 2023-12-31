from selenium import webdriver
import time
from datetime import date
from selenium.webdriver.common.by import By
import pandas as pd


def load_products(stats, driver, all_products, base_url, category, price_lower_bound_threshold=1000):
    page=1
    while True:
        driver.get(base_url.replace('{i}',str(page)))
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        products = driver.find_elements(By.CSS_SELECTOR, "ul.products")
        if len(products)==0:
            break
        products=products[0]
        lista=products.find_elements(By.CSS_SELECTOR, "li")
        for l in lista:
            name_element=l.find_element(By.CSS_SELECTOR, "div.product-name > a")
            name=name_element.text
            link=name_element.get_attribute('href')
            image=l.find_element(By.CSS_SELECTOR, "img.products-img").get_attribute('src')
            price=l.find_element(By.CSS_SELECTOR, ".product-price").find_element(By.CSS_SELECTOR, 'strong > span').text

            product_row=dict()
            product_row['name']=name
            product_row['link']=link
            product_row['image']=image
            product_row['regular_price']=int(price.replace(',',''))
            if product_row['regular_price']<price_lower_bound_threshold:
                continue
            product_row['category']=category
            all_products.append(product_row)
            stats[category]+=1
        page+=1
        time.sleep(1)

def scrape_data(folder_path):
    driver = webdriver.Firefox()
    all_products=list()
    stats={
        'LAPTOP': 0,
        'PHONE': 0,
        'TV': 0,
        'GPU': 0,
        'CPU': 0,
        'AC': 0,
        'FRIDGE': 0,
        'FREEZER': 0
    }
    load_products(stats, driver, all_products, "https://www.anhoch.com/category/3003/prenosni-kompjuteri-laptopi#page/{i}/offset/64/",'LAPTOP')
    load_products(stats, driver,all_products, "https://www.anhoch.com/category/3017/smartfoni-i-mobilni-tel#page/{i}/offset/64/",'PHONE', price_lower_bound_threshold=3000)
    load_products(stats, driver,all_products, 'https://www.anhoch.com/category/1013/televizori#page/{i}/offset/64/', 'TV')
    load_products(stats, driver,all_products, "https://www.anhoch.com/category/374/grafichki-kartichki#page/{i}/offset/64/",'GPU', price_lower_bound_threshold=3000)
    load_products(stats, driver,all_products, "https://www.anhoch.com/category/3004/intel-procesori#page/{i}/offset/64/",'CPU')
    load_products(stats, driver,all_products, "https://www.anhoch.com/category/3005/amd-procesori#page/{i}/offset/64/",'CPU')
    load_products(stats, driver,all_products, "https://www.anhoch.com/category/1030/klima-uredi#page/{i}/offset/64/",'AC')
    # NO FRIDGES AND FREEZERS AVAILABLE ON ANHOCH

    df=pd.DataFrame.from_dict(all_products)
    df['store']='Anhoch'
    df['date']= date.today()
    file_name=f"{folder_path}\\anhoch_{date.today()}.csv"
    df.to_csv(file_name, index=False)
    driver.quit()
    return file_name, stats


from selenium import webdriver
import time
from datetime import date
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Firefox()

def load_products(all_products, base_url, category, price_lower_bound_threshold=1000):
    page=1
    while True:
        driver.get(base_url.replace('{i}',str(page)))
        time.sleep(2)
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
        page+=1
        time.sleep(1)

def scrape_data():
    all_products=list()
    load_products(all_products, "https://www.anhoch.com/category/3003/prenosni-kompjuteri-laptopi#page/{i}/offset/64/",'Laptop')
    load_products(all_products, "https://www.anhoch.com/category/3017/smartfoni-i-mobilni-tel#page/{i}/offset/64/",'Phone', price_lower_bound_threshold=3000)
    load_products(all_products, 'https://www.anhoch.com/category/1013/televizori#page/{i}/offset/64/', 'TV')
    load_products(all_products, "https://www.anhoch.com/category/374/grafichki-kartichki#page/{i}/offset/64/",'GPU', price_lower_bound_threshold=3000)
    load_products(all_products, "https://www.anhoch.com/category/3004/intel-procesori#page/{i}/offset/64/",'CPU')
    load_products(all_products, "https://www.anhoch.com/category/3005/amd-procesori#page/{i}/offset/64/",'CPU')
    load_products(all_products, "https://www.anhoch.com/category/1030/klima-uredi#page/{i}/offset/64/",'Air Conditioner')
    # NO FRIDGES AND FREEZERS AVAILABLE ON ANHOCH

    df=pd.DataFrame.from_dict(all_products)
    df['store']='Anhoch'
    df['date']= date.today()
    print(df)
    df.to_excel(f"anhoch_{date.today()}.xlsx", index=False)
    driver.quit()

scrape_data()



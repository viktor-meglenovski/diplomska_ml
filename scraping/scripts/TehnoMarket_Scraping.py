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
        product_row=dict()
        name_element=l.find_element(By.CSS_SELECTOR, "div.product-name > a")
        name=name_element.text
        link=name_element.get_attribute('href')
        image=l.find_element(By.CSS_SELECTOR, ".product-figure").get_attribute('style')
        image=image.split(' ')[1][5:-3]
        regular_price=l.find_element(By.CSS_SELECTOR, ".product-price > .pull-left > div > strong > .nm").text
        discount_price=None
        discount_price=l.find_elements(By.CSS_SELECTOR, ".smart-products")
        if len(discount_price) > 0:
            discount_price=discount_price[0].find_element(By.CSS_SELECTOR, "strong > .nm")
            discount_price=discount_price.text
            product_row['discount_price']=int(discount_price.replace(',',''))
        else:
            product_row['discount_price']=None
        product_row['name']=name.strip()
        product_row['link']=link
        product_row['image']=image
        product_row['regular_price']=int(regular_price.replace(',',''))
        if product_row['regular_price']<price_lower_bound_threshold:
            continue
        product_row['category']=category
        all_products.append(product_row)
    page+=1
    time.sleep(1)

def scrape_data():
    all_products=list()
    load_products(all_products, 'https://tehnomarket.com.mk/category/4003/laptopi#page/{i}/offset/64/', 'LAPTOP')
    load_products(all_products, 'https://tehnomarket.com.mk/category/4109/mobilni-telefoni#page/{i}/offset/64/', 'PHONE', price_lower_bound_threshold=3000)
    load_products(all_products, 'https://tehnomarket.com.mk/category/4335/televizori#page/{i}/offset/64/', 'TV', price_lower_bound_threshold=10000)
    load_products(all_products, 'https://tehnomarket.com.mk/category/3791/klima-uredi#page/{i}/offset/64/', 'AC', price_lower_bound_threshold=20000)
    load_products(all_products, 'https://tehnomarket.com.mk/category/3886/ladilnici#page/{i}/offset/64/', 'FRIDGE')
    load_products(all_products, 'https://tehnomarket.com.mk/category/3884/zamrznuvachi#page/{i}/offset/64/', 'FREEZERS')
    # NO GPU AND CPU AVAILABLE ON TEHNOMARKET

    df=pd.DataFrame.from_dict(all_products)
    df['store']='TehnoMarket'
    df['date']= date.today()
    df=df[['name','category','store', 'link', 'image', 'regular_price', 'discount_price', 'date']]
    print(df)
    df.to_excel(f"tehnomarket_{date.today()}.xlsx", index=False)
    driver.quit()

scrape_data()
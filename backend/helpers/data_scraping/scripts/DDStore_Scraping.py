import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from datetime import date

def load_products(all_products, base_url, category, price_lower_bound_threshold=1000):
  page=1
  while True:
    url=base_url.replace('{i}',str(page))
    req=Request(url, headers={'User-Agent':'Mozilla/5.0'})
    webpage=urlopen(req).read()
    page_soup=soup(webpage,"html.parser")
    products=page_soup.select("ol.products > li.product-item")
    if not products:
      break
    for p in products:
      name_element=p.select('a.product-item-link')
      image_element=p.select('.product-image-photo ')
      price_element=p.select('span.price')
      if(len(name_element)==0 or len(image_element)==0 or len(price_element)==0):
        continue
      product_row=dict()
      product_row['name']=name_element[0].text.strip()
      product_row['link']=name_element[0].get('href')
      product_row['image']=image_element[0].get('src')
      product_row['regular_price']=int(price_element[0].text.split(" ")[0].replace('.',''))
      if(product_row['regular_price'])<price_lower_bound_threshold:
        continue
      product_row['category']=category
      all_products.append(product_row)
    page+=1

def scrape_data(folder_path):
    all_products=list()
    load_products(all_products, 'https://ddstore.mk/computersandlaptops/notebooksandaccessories/notebooks.html?p={i}&product_list_limit=48', 'LAPTOP')
    load_products(all_products, 'https://ddstore.mk/computersandlaptops/SmartphonesandAccessories/smartphones.html?p={i}&product_list_limit=48', 'PHONE', price_lower_bound_threshold=3000)
    load_products(all_products, 'https://ddstore.mk/MonitorsTVandProjectors/TelevisionsandEquipment/televisions.html?p={i}&product_list_limit=48', 'TV')
    load_products(all_products, 'https://ddstore.mk/computercomponents/graphiccards.html?p={i}&product_list_limit=48', 'GPU', price_lower_bound_threshold=2000)
    load_products(all_products, 'https://ddstore.mk/computercomponents/processors.html?p={i}&product_list_limit=48', 'CPU')
    # NO AIR CONDITIONERS, FRIDGES AND FREEZERS AVAILABLE ON DDSTORE

    df=pd.DataFrame.from_dict(all_products)
    df['store']='DDStore'
    df['date']= date.today()
    df.to_csv(f"{folder_path}\\ddstore_{date.today()}.csv", index=False)
import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from datetime import date

def load_products(all_products, base_url, category, price_lower_bound_threshold=1000):
  page=1
  while True:
    url=f'{base_url}{page}'
    req=Request(url, headers={'User-Agent':'Mozilla/5.0'})
    webpage=urlopen(req).read()
    page_soup=soup(webpage,"html.parser")
    products=page_soup.select(".product")
    if not products:
      break
    for p in products:
      name_element=p.select('#mora_da_ima_prazno_mesto a')
      image_element=p.select('.zoom-image-effect')
      code_element=p.select('.shifra')
      price_element=p.select('.category-price-redovna .price-old-new')
      discount_price_element=p.select('.category-price-akciska .price-new-new')
      if(len(name_element)==0 or len(image_element)==0 or len(code_element)==0 or len(price_element)==0 or len(discount_price_element)==0):
        continue
      product_row=dict()
      product_row['name']=name_element[0].text.strip()
      product_row['link']=name_element[0].get('href')
      product_row['image']=image_element[0].get('data-echo')
      product_row['code']=int(code_element[0].text.replace('Шифра: ',''))
      product_row['regular_price']=int(price_element[0].text.split(" ")[0].replace(',',''))
      if(product_row['regular_price'])<price_lower_bound_threshold:
        continue
      product_row['discount_price']=int(discount_price_element[0].text.split(" ")[0].replace(',',''))
      product_row['category']=category
      all_products.append(product_row)
    page+=1

def scrape_data():
    all_products=list()
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10002_10003&limit=100&page=', 'LAPTOP')
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10066_10067&limit=100&page=', 'PHONE', price_lower_bound_threshold=3000)
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10054_10055&limit=100&page=', 'TV')
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10019_10020_10025&limit=100&page=', 'GPU', price_lower_bound_threshold=3000)
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10019_10020_10021&limit=100&page=', 'CPU')
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10169_10170&limit=100&page=', 'AC')
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10090_10096&limit=100&page=', 'FRIDGE')
    load_products(all_products, 'https://setec.mk/index.php?route=product/category&path=10090_10101&limit=100&page=', 'FREEZERS')
    df=pd.DataFrame.from_dict(all_products)
    df['store']='Setec'
    df['date']= date.today()
    print(df)
    df.to_excel(f"setec_{date.today()}.xlsx", index=False)

scrape_data()
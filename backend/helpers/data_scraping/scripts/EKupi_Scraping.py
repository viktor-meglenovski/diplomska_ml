import pandas as pd
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from datetime import date


def load_products(stats, all_products, base_url, category, price_lower_bound_threshold=1000):
    page = 0
    while True:
        url = f"{base_url}{str(page)}"
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        page_soup = soup(webpage, "html.parser")
        products = page_soup.select("div.product-item")
        if not products:
            break
        for p in products:
            name_element = p.select('a.name')
            image_element = p.select('.thumb > img')
            price_element = p.select('div.price')
            if (len(name_element) == 0 or len(image_element) == 0 or len(price_element) == 0):
                continue
            product_row = dict()
            product_row['name'] = name_element[0].text.strip()
            product_row['link'] = name_element[0].get('href')
            product_row['image'] = image_element[0].get('src')
            product_row['regular_price'] = int(price_element[0].text.strip()[:-4].replace('.', ''))
            if (product_row['regular_price']) < price_lower_bound_threshold:
                continue
            product_row['category'] = category
            all_products.append(product_row)
            stats[category] += 1
        page += 1


def scrape_data(folder_path):
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
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%9A%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8/%D0%9B%D0%B0%D0%BF%D1%82%D0%BE%D0%BF%D0%B8-%D0%B8-%D0%BE%D0%BF%D1%80%D0%B5%D0%BC%D0%B0/%D0%9B%D0%B0%D0%BF%D1%82%D0%BE%D0%BF%D0%B8/c/10068?q=%3Arelevance&page=',
                  'LAPTOP')
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%95%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%BE%D0%BD%D0%B8%D0%BA%D0%B0/%D0%9C%D0%BE%D0%B1%D0%B8%D0%BB%D0%BD%D0%B8-%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD%D0%B8-%D0%B8-%D0%B4%D0%BE%D0%B4%D0%B0%D1%82%D0%BE%D1%86%D0%B8/%D0%A1%D0%BC%D0%B0%D1%80%D1%82%D1%84%D0%BE%D0%BD%D0%B8/c/10087?q=%3Arelevance&page=',
                  'PHONE', price_lower_bound_threshold=3000)
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%95%D0%BB%D0%B5%D0%BA%D1%82%D1%80%D0%BE%D0%BD%D0%B8%D0%BA%D0%B0/%D0%A2%D0%B5%D0%BB%D0%B5%D0%B2%D0%B8%D0%B7%D0%BE%D1%80%D0%B8-%D0%B8-%D0%BE%D0%BF%D1%80%D0%B5%D0%BC%D0%B0/T%D0%B5%D0%BB%D0%B5%D0%B2%D0%B8%D0%B7%D0%BE%D1%80%D0%B8/c/10579?q=%3Arelevance&page=',
                  'TV')
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%9A%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8/%D0%9A%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8-%D0%B8-%D0%BF%D0%B5%D1%80%D0%B8%D1%84%D0%B5%D1%80%D0%B8%D1%98%D0%B0/K%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D1%81%D0%BA%D0%B8-%D0%BA%D0%BE%D0%BC%D0%BF%D0%BE%D0%BD%D0%B5%D0%BD%D1%82%D0%B8/%D0%93%D1%80%D0%B0%D1%84%D0%B8%D1%87%D0%BA%D0%B8-%D0%BA%D0%B0%D1%80%D1%82%D0%B8/c/10541?q=%3Arelevance&page=',
                  'GPU')
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%9A%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8/%D0%9A%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D0%B8-%D0%B8-%D0%BF%D0%B5%D1%80%D0%B8%D1%84%D0%B5%D1%80%D0%B8%D1%98%D0%B0/K%D0%BE%D0%BC%D0%BF%D1%98%D1%83%D1%82%D0%B5%D1%80%D1%81%D0%BA%D0%B8-%D0%BA%D0%BE%D0%BC%D0%BF%D0%BE%D0%BD%D0%B5%D0%BD%D1%82%D0%B8/%D0%9F%D1%80%D0%BE%D1%86%D0%B5%D1%81%D0%BE%D1%80%D0%B8/c/10549?q=%3Arelevance&page=',
                  'CPU')
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%90%D0%BF%D0%B0%D1%80%D0%B0%D1%82%D0%B8-%D0%B7%D0%B0-%D0%B4%D0%BE%D0%BC%D0%B0%D1%9C%D0%B8%D0%BD%D1%81%D1%82%D0%B2%D0%BE/%D0%93%D1%80%D0%B5%D0%B5%D1%9A%D0%B5-%D0%B8-%D0%BB%D0%B0%D0%B4%D0%B5%D1%9A%D0%B5/%D0%9A%D0%BB%D0%B8%D0%BC%D0%B0-%D1%83%D1%80%D0%B5%D0%B4%D0%B8/%D0%9A%D0%BB%D0%B8%D0%BC%D0%B0-%D1%83%D1%80%D0%B5%D0%B4%D0%B8-%D0%B7%D0%B0-%D0%B4%D0%BE%D0%BC/c/10163?q=%3Arelevance&page=',
                  'AC')
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%90%D0%BF%D0%B0%D1%80%D0%B0%D1%82%D0%B8-%D0%B7%D0%B0-%D0%B4%D0%BE%D0%BC%D0%B0%D1%9C%D0%B8%D0%BD%D1%81%D1%82%D0%B2%D0%BE/%D0%91%D0%B5%D0%BB%D0%B0-%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0/%D0%A4%D1%80%D0%B8%D0%B6%D0%B8%D0%B4%D0%B5%D1%80%D0%B8/c/10130?q=%3Arelevance&page=',
                  'FRIDGE')
    load_products(stats, all_products,
                  'https://www.ekupi.mk/mk/%D0%90%D0%BF%D0%B0%D1%80%D0%B0%D1%82%D0%B8-%D0%B7%D0%B0-%D0%B4%D0%BE%D0%BC%D0%B0%D1%9C%D0%B8%D0%BD%D1%81%D1%82%D0%B2%D0%BE/%D0%91%D0%B5%D0%BB%D0%B0-%D1%82%D0%B5%D1%85%D0%BD%D0%B8%D0%BA%D0%B0/%D0%97%D0%B0%D0%BC%D1%80%D0%B7%D0%BD%D1%83%D0%B2%D0%B0%D1%87%D0%B8/c/10131?q=%3Arelevance&page=',
                  'FREEZER')
    # NO AIR CONDITIONERS, FRIDGES AND FREEZERS AVAILABLE ON DDSTORE
    df = pd.DataFrame.from_dict(all_products)
    df['store'] = 'EKupi'
    df['date'] = date.today()
    file_name = f"{folder_path}\\ekupi_{date.today()}.csv"
    df.to_csv(file_name, index=False)
    return file_name, stats

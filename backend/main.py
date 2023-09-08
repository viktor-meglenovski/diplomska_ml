from fastapi import FastAPI

from helpers.data_scraping.scripts.scrape_all import scrape_all
from helpers.populate_database import populate_products

app = FastAPI()


@app.get("/")
async def root():
    populate_products()
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/admin/scrape_data")
async def scrape_data():
    # scrape_all()
    return {"message": "Scraping Complete"}

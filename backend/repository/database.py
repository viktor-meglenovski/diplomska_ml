from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

# Access environment variables
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')

connection_url = f"postgresql://{LOGIN}:{PASSWORD}@localhost:5432/diplomska"

engine = create_engine(connection_url)
Session = sessionmaker(bind=engine)

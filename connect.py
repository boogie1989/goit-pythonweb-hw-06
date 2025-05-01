"""Setup database connection using SQLAlchemy."""

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "567234")
DB_NAME = os.getenv("DB_NAME", "database_name")
DB_PORT = os.getenv("DB_PORT", "5432")

URL_TO_DB = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(URL_TO_DB)
Session = sessionmaker(bind=engine)
session = Session()

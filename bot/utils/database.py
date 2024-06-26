from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)
metadata = MetaData()

keys = Table(
    "keys",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String, index=True),
    Column("server", String),
    Column("port", Integer),
    Column("password", String),
    Column("method", String),
    Column("exp_start", DateTime),
    Column("exp_end", DateTime),
    Column("type", String),
    Column("config_url", String)
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

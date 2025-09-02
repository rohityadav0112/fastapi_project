from sqlalchemy.orm import sessionmaker
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine



db_url="mysql://root:123456@localhost:3306/RohitTable"
engine= create_engine(db_url)

session = sessionmaker(autocommit=False,autoflush=False,bind=engine)
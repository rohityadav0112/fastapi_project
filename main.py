from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pymysql

from models import Product
from database import session, engine
import database_models

pymysql.install_as_MySQLdb()

app = FastAPI()

# ✅ Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Create DB tables
database_models.Base.metadata.create_all(bind=engine)

# Preloaded products
products = [
    Product(name="phone", des="budget iphone", price=99, quantity=10),
    Product(name="Laptop", des="budget Lappy", price=100099, quantity=5),
]


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = session()
    try:
        count = db.query(database_models.Product).count()
        if count == 0:
            for product in products:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()


# ✅ Run init_db at startup
init_db()


@app.get("/")
def greet():
    return {"message": "Hello welcome Rohit"}


@app.get("/products/")  # ✅ trailing slash
def get_all_products(db: Session = Depends(get_db)):
    return db.query(database_models.Product).all()


@app.get("/products/{id}")
def get_product_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product
    return {"error": "Product not found"}


@app.post("/products/")  # ✅ trailing slash
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # get ID
    return db_product


@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.des = product.des
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return {"message": "Product updated"}
    else:
        return {"error": "No Product Found"}


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"message": "Product deleted successfully"}
    else:
        return {"error": "Product not found"}

from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter, Request
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from TodoApp.models.modelProduct import Product
from models.modelUser import Base
from TodoApp.database import SessionLocal, engine


router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
Base.metadata.create_all(bind=engine)


class Product(BaseModel):
    pass


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    summary='List all products'
)
async def get_all_products(db: db_dependency):
    product_model = db.query(Product).all()

    if product_model is not None:
        return product_model
    else:
        raise http_exception("Product not found")


@router.get(path='/product/{todo_id}',
            status_code=status.HTTP_200_OK,
            summary='One product',
            )
async def get_product_by_id(db: db_dependency, product_id: Path(gt=0)):
    product_model = db.query(Product).filter(Product.product_id == product_id).first()

    if product_model is not None:
        db.add(product_model)
        db.commit()

def http_exception(message: str):
    return HTTPException(status_code=404, detail=message)

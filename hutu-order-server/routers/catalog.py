"""目录接口：餐厅 / 档口 / 餐品 / 优惠券"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Coupon, Product, Stall, Store
from schemas import CouponOut, ProductOut, StallOut, StoreOut
from utils import ok

router = APIRouter(prefix="/api/catalog", tags=["目录"])


@router.get("/stores")
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).order_by(Store.distance).all()
    return ok([StoreOut.model_validate(s).model_dump(mode="json") for s in stores])


@router.get("/stalls")
def list_stalls(db: Session = Depends(get_db)):
    stalls = db.query(Stall).filter(Stall.is_active == True).order_by(Stall.code).all()
    return ok([StallOut.model_validate(s).model_dump(mode="json") for s in stalls])


@router.get("/products")
def list_products(stall_id: str = "", db: Session = Depends(get_db)):
    q = db.query(Product).order_by(Product.sales.desc())
    if stall_id:
        q = q.filter(Product.stall_id == stall_id)
    products = q.all()
    return ok([ProductOut.model_validate(p).model_dump(mode="json") for p in products])


@router.get("/coupons")
def list_coupons(db: Session = Depends(get_db)):
    coupons = db.query(Coupon).filter(Coupon.is_active == True).order_by(Coupon.threshold_cents).all()
    return ok([CouponOut.model_validate(c).model_dump(mode="json") for c in coupons])

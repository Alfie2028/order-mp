"""商家端接口：订单管理（接单 / 出餐）+ 经营管理（商品/档口/优惠券/营业状态/看板/上传）"""
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Coupon, Order, Product, Stall, Store, User
from schemas import CouponIn, CouponOut, OrderOut, ProductIn, ProductOut, StallIn, StallOut
from utils import ok

router = APIRouter(prefix="/api/merchant", tags=["商家"])

MAIN_STORE_ID = "henau-canteen"

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
_CONTENT_TYPE_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
}


def _ext_for(content_type):
    return _CONTENT_TYPE_EXT.get((content_type or "").lower(), ".jpg")


def _to_out(order: Order) -> dict:
    return OrderOut.model_validate(order).model_dump(mode="json")


def _require_merchant(user: User):
    if user.role != "merchant":
        raise HTTPException(status_code=403, detail="无商家权限")


@router.get("/orders")
def list_merchant_orders(status: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """商家订单列表，可按状态筛选（pending/paid/making/ready/completed）"""
    _require_merchant(user)
    q = db.query(Order).order_by(Order.created_at.desc())
    if status:
        q = q.filter(Order.status == status)
    return ok([_to_out(o) for o in q.all()])


@router.post("/orders/{order_id}/accept")
def accept_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """接单：paid -> making"""
    _require_merchant(user)
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail=f"订单状态为「{order.status_text}」，无法接单")
    order.status, order.status_text = "making", "制作中"
    db.commit()
    db.refresh(order)
    return ok(_to_out(order))


@router.post("/orders/{order_id}/ready")
def ready_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """出餐：making -> ready"""
    _require_merchant(user)
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "making":
        raise HTTPException(status_code=400, detail=f"订单状态为「{order.status_text}」，无法出餐")
    order.status, order.status_text = "ready", "待取餐"
    db.commit()
    db.refresh(order)
    return ok(_to_out(order))


# ================= 餐品管理 =================
@router.get("/products")
def list_merchant_products(stall_id: str = "", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    q = db.query(Product).order_by(Product.stall_id, Product.sales.desc())
    if stall_id:
        q = q.filter(Product.stall_id == stall_id)
    return ok([ProductOut.model_validate(p).model_dump(mode="json") for p in q.all()])


@router.post("/products")
def create_product(body: ProductIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    if not db.get(Stall, body.stall_id):
        raise HTTPException(status_code=400, detail="档口不存在")
    product = Product(id="p" + uuid.uuid4().hex[:12], **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return ok(ProductOut.model_validate(product).model_dump(mode="json"))


@router.put("/products/{product_id}")
def update_product(product_id: str, body: ProductIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="餐品不存在")
    if not db.get(Stall, body.stall_id):
        raise HTTPException(status_code=400, detail="档口不存在")
    for k, v in body.model_dump().items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    return ok(ProductOut.model_validate(product).model_dump(mode="json"))


@router.delete("/products/{product_id}")
def delete_product(product_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="餐品不存在")
    db.delete(product)
    db.commit()
    return ok({"deleted": True})


@router.post("/products/{product_id}/toggle")
def toggle_product(product_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="餐品不存在")
    product.is_active = not product.is_active
    db.commit()
    db.refresh(product)
    return ok(ProductOut.model_validate(product).model_dump(mode="json"))


# ================= 档口管理 =================
@router.get("/stalls")
def list_merchant_stalls(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    stalls = db.query(Stall).order_by(Stall.code).all()
    return ok([StallOut.model_validate(s).model_dump(mode="json") for s in stalls])


@router.post("/stalls")
def create_stall(body: StallIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    data = body.model_dump()
    if not data.get("code"):
        data["code"] = (db.query(func.max(Stall.code)).scalar() or 0) + 1
    stall = Stall(id="s" + uuid.uuid4().hex[:8], **data)
    db.add(stall)
    db.commit()
    db.refresh(stall)
    return ok(StallOut.model_validate(stall).model_dump(mode="json"))


@router.put("/stalls/{stall_id}")
def update_stall(stall_id: str, body: StallIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    stall = db.get(Stall, stall_id)
    if not stall:
        raise HTTPException(status_code=404, detail="档口不存在")
    for k, v in body.model_dump().items():
        setattr(stall, k, v)
    db.commit()
    db.refresh(stall)
    return ok(StallOut.model_validate(stall).model_dump(mode="json"))


@router.post("/stalls/{stall_id}/toggle")
def toggle_stall(stall_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    stall = db.get(Stall, stall_id)
    if not stall:
        raise HTTPException(status_code=404, detail="档口不存在")
    stall.is_active = not stall.is_active
    db.commit()
    db.refresh(stall)
    return ok(StallOut.model_validate(stall).model_dump(mode="json"))


# ================= 优惠券管理 =================
@router.get("/coupons")
def list_merchant_coupons(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    coupons = db.query(Coupon).order_by(Coupon.threshold_cents).all()
    return ok([CouponOut.model_validate(c).model_dump(mode="json") for c in coupons])


@router.post("/coupons")
def create_coupon(body: CouponIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    coupon = Coupon(id="c" + uuid.uuid4().hex[:8], **body.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return ok(CouponOut.model_validate(coupon).model_dump(mode="json"))


@router.post("/coupons/{coupon_id}/toggle")
def toggle_coupon(coupon_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    coupon = db.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")
    coupon.is_active = not coupon.is_active
    db.commit()
    db.refresh(coupon)
    return ok(CouponOut.model_validate(coupon).model_dump(mode="json"))


# ================= 营业状态 =================
@router.post("/store/toggle")
def toggle_store(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    store = db.get(Store, MAIN_STORE_ID)
    if not store:
        raise HTTPException(status_code=404, detail="店铺不存在")
    store.status = "closed" if store.status != "closed" else "open"
    db.commit()
    db.refresh(store)
    return ok({"id": store.id, "status": store.status})


# ================= 营业数据看板 =================
@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_merchant(user)
    today = datetime.now(timezone.utc).replace(tzinfo=None).date()
    start = datetime.combine(today, datetime.min.time())
    orders = db.query(Order).all()
    statuses = {}
    today_count = 0
    today_sales = 0
    for o in orders:
        statuses[o.status] = statuses.get(o.status, 0) + 1
        if o.created_at >= start:
            today_count += 1
            if o.status in ("paid", "making", "ready", "completed"):
                today_sales += o.total_cents
    return ok({
        "today_orders": today_count,
        "today_sales_cents": today_sales,
        "status_counts": statuses,
        "pending_count": statuses.get("pending", 0),
        "paid_count": statuses.get("paid", 0),
        "making_count": statuses.get("making", 0),
        "ready_count": statuses.get("ready", 0),
        "completed_count": statuses.get("completed", 0),
    })


# ================= 图片上传 =================
@router.post("/upload")
def upload_image(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    """商品图片上传：保存到 uploads/ 目录，返回相对路径 /uploads/<filename>"""
    _require_merchant(user)
    data = file.file.read()
    filename = f"{uuid.uuid4().hex}{_ext_for(file.content_type)}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(data)
    return ok({"url": f"/uploads/{filename}"})

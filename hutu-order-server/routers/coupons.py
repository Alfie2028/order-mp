"""用户优惠券接口：我的券 / 领取"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models import Coupon, User, UserCoupon
from schemas import CouponOut
from utils import ok

router = APIRouter(prefix="/api/coupons", tags=["优惠券"])


@router.get("/mine")
def my_coupons(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """当前用户已领取且仍有效的券"""
    rows = (
        db.query(Coupon)
        .join(UserCoupon, UserCoupon.coupon_id == Coupon.id)
        .filter(UserCoupon.user_id == user.id, Coupon.is_active == True)
        .order_by(Coupon.threshold_cents)
        .all()
    )
    return ok([CouponOut.model_validate(c).model_dump(mode="json") for c in rows])


@router.post("/{coupon_id}/claim")
def claim_coupon(coupon_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """领取优惠券（幂等：已领取直接返回该券）"""
    coupon = db.get(Coupon, coupon_id)
    if not coupon or not coupon.is_active:
        raise HTTPException(status_code=404, detail="优惠券不存在或已停用")
    existing = db.query(UserCoupon).filter(
        UserCoupon.user_id == user.id, UserCoupon.coupon_id == coupon_id
    ).first()
    if not existing:
        db.add(UserCoupon(user_id=user.id, coupon_id=coupon_id))
        db.commit()
    return ok(CouponOut.model_validate(coupon).model_dump(mode="json"))

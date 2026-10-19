"""SQLAlchemy ORM 模型：8 张核心表"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Integer, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def utcnow():
    """返回不带时区信息的 UTC 当前时间，避免 SQLite 存储时区偏移"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # 昵称/展示名（注册时取邮箱前缀）
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)    # 登录标识（邮箱）
    password_hash: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(20), default="user")  # user / merchant / admin
    points: Mapped[int] = mapped_column(Integer, default=0)
    avatar: Mapped[str] = mapped_column(Text, default="")  # 头像 Base64 data URL，可空（不强制设置）
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class EmailCode(Base):
    """邮箱验证码：落库存储，使用后标记 used，超过 expires_at 即失效"""
    __tablename__ = "email_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(120), index=True)
    code: Mapped[str] = mapped_column(String(6))
    purpose: Mapped[str] = mapped_column(String(20))  # register / login
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    short_name: Mapped[str] = mapped_column(String(50), default="")
    address: Mapped[str] = mapped_column(String(200), default="")
    distance: Mapped[int] = mapped_column(Integer, default=0)
    hours: Mapped[str] = mapped_column(String(50), default="")
    status: Mapped[str] = mapped_column(String(20), default="open")
    wait_minutes: Mapped[int] = mapped_column(Integer, default=0)
    latitude: Mapped[float] = mapped_column(Float, default=0.0)
    longitude: Mapped[float] = mapped_column(Float, default=0.0)
    image: Mapped[str] = mapped_column(String(200), default="")


class Stall(Base):
    __tablename__ = "stalls"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    store_id: Mapped[str] = mapped_column(String(50), ForeignKey("stores.id"))
    name: Mapped[str] = mapped_column(String(50))
    short_name: Mapped[str] = mapped_column(String(20), default="")
    description: Mapped[str] = mapped_column(String(200), default="")
    code: Mapped[int] = mapped_column(Integer, default=0)  # 档口编号 1-6，参与取餐码生成
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # 上架/下架


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    stall_id: Mapped[str] = mapped_column(String(50), ForeignKey("stalls.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    subtitle: Mapped[str] = mapped_column(String(200), default="")
    price_cents: Mapped[int] = mapped_column(Integer)
    original_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    badge: Mapped[str] = mapped_column(String(50), default="")
    sales: Mapped[int] = mapped_column(Integer, default=0)
    image: Mapped[str] = mapped_column(Text, default="")  # 图片：静态路径 /static/xxx 或 Base64 data URL（存数据库）
    options: Mapped[str] = mapped_column(Text, default="[]")  # JSON 字符串，规格选项
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # 上架/下架


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    store_id: Mapped[str] = mapped_column(String(50), default="")
    stall_id: Mapped[str] = mapped_column(String(50), default="")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    status_text: Mapped[str] = mapped_column(String(20), default="待支付")
    pickup_code: Mapped[str] = mapped_column(String(10), default="")
    mode: Mapped[str] = mapped_column(String(10), default="pickup")  # pickup / dineIn
    remark: Mapped[str] = mapped_column(String(200), default="")
    subtotal_cents: Mapped[int] = mapped_column(Integer, default=0)
    discount_cents: Mapped[int] = mapped_column(Integer, default=0)
    total_cents: Mapped[int] = mapped_column(Integer, default=0)
    coupon_name: Mapped[str] = mapped_column(String(50), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[str] = mapped_column(String(50), default="")
    name: Mapped[str] = mapped_column(String(100), default="")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    options: Mapped[str] = mapped_column(Text, default="[]")  # JSON 字符串

    order: Mapped["Order"] = relationship(back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    aoid: Mapped[str] = mapped_column(String(100), default="")  # BufPay 平台订单号
    pay_type: Mapped[str] = mapped_column(String(20), default="")  # alipay / wechat
    amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending / paid / mock
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    threshold_cents: Mapped[int] = mapped_column(Integer, default=0)   # 满减门槛（分）
    discount_cents: Mapped[int] = mapped_column(Integer, default=0)    # 优惠金额（分）
    expires: Mapped[str] = mapped_column(String(20), default="")       # 有效期，如 2026-12-31
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)     # 启用/停用


class UserCoupon(Base):
    """用户已领取的优惠券：领取后可于结算时使用"""
    __tablename__ = "user_coupons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    coupon_id: Mapped[str] = mapped_column(String(50), ForeignKey("coupons.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Review(Base):
    """订单评价 + 评分：一个订单仅可评价一次"""
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int] = mapped_column(Integer, default=5)  # 1~5 星
    content: Mapped[str] = mapped_column(Text, default="")   # 文字评价
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[str] = mapped_column(String(50), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[str] = mapped_column(String(50), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    options: Mapped[str] = mapped_column(Text, default="[]")  # JSON 字符串
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

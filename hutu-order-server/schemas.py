"""Pydantic 请求/响应模型"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---- 认证 ----
class SendCodeRequest(BaseModel):
    email: EmailStr
    purpose: str = Field(default="register", pattern="^(register|login)$")


class UserRegister(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class LoginByCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str = ""
    role: str
    points: int
    avatar: str = ""


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---- 目录 ----
class StoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    short_name: str
    address: str
    distance: int
    hours: str
    status: str
    wait_minutes: int
    latitude: float
    longitude: float
    image: str


class StallOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    store_id: str
    name: str
    short_name: str
    description: str
    code: int
    is_active: bool


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    stall_id: str
    name: str
    subtitle: str
    price_cents: int
    original_price_cents: int
    badge: str
    sales: int
    image: str
    options: str
    is_active: bool


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    threshold_cents: int
    discount_cents: int
    expires: str
    is_active: bool


# ---- 商家管理入参 ----
class CouponIn(BaseModel):
    name: str
    threshold_cents: int = 0
    discount_cents: int = 0
    expires: str = ""


class StallIn(BaseModel):
    store_id: str = "henau-canteen"
    name: str
    short_name: str = ""
    description: str = ""
    code: int = 0


class ProductIn(BaseModel):
    stall_id: str
    name: str
    subtitle: str = ""
    price_cents: int
    original_price_cents: int = 0
    badge: str = ""
    image: str = ""
    options: str = "[]"


# ---- 订单 ----
class OrderItemIn(BaseModel):
    product_id: str
    name: str
    quantity: int = 1
    unit_price_cents: int
    options: str = "[]"


class OrderCreate(BaseModel):
    stall_id: str
    store_id: str = ""
    mode: str = "pickup"
    remark: str = ""
    coupon_id: str = ""
    items: List[OrderItemIn]


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: str
    name: str
    quantity: int
    unit_price_cents: int
    options: str


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_no: str
    store_id: str
    stall_id: str
    status: str
    status_text: str
    pickup_code: str
    mode: str
    remark: str
    subtotal_cents: int
    discount_cents: int
    total_cents: int
    coupon_name: str
    created_at: datetime
    paid_at: Optional[datetime]
    items: List[OrderItemOut]


class PayResultOut(BaseModel):
    """支付下单结果：真实 BufPay 返回二维码，模拟模式直接标记成功"""
    mode: str  # mock / bufpay
    paid: bool
    qr_img: str = ""      # BufPay base64 二维码（仅 bufpay 模式）
    pay_url: str = ""     # BufPay 跳转链接（仅 bufpay 模式）
    aoid: str = ""        # BufPay 平台订单号（仅 bufpay 模式）


# ---- 评价 ----
class ReviewIn(BaseModel):
    order_id: int
    rating: int = 5
    content: str = ""


# ---- 购物车 / 收藏 ----
class CartItemIn(BaseModel):
    product_id: str
    quantity: int = 1
    options: str = "[]"   # JSON 字符串（规格选择）


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: str
    quantity: int
    options: str

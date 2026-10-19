"""FastAPI 入口：应用初始化、路由注册、全局异常、CORS"""
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from database import Base, engine
import models  # noqa: 确保 ORM 模型注册到 metadata
from routers import auth, cart, catalog, coupons, favorite, merchant, order, pay, review

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="校园点餐后端",
    description="基于 FastAPI + SQLite 的校园多档口点餐后端（bcrypt + JWT + BufPay 预留）",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(coupons.router)
app.include_router(order.router)
app.include_router(pay.router)
app.include_router(favorite.router)
app.include_router(cart.router)
app.include_router(merchant.router)
app.include_router(review.router)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 异常统一转为 {code, msg, data} 格式"""
    return JSONResponse(status_code=exc.status_code,
                        content={"code": exc.status_code, "msg": str(exc.detail), "data": None})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """未捕获异常统一兜底，不向客户端暴露堆栈"""
    return JSONResponse(status_code=500,
                        content={"code": 500, "msg": f"服务器错误: {exc}", "data": None})


@app.get("/")
def root():
    return {"code": 0, "msg": "ok", "data": "校园点餐后端运行中，接口文档见 /docs"}

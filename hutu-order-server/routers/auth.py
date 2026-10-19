"""认证接口：邮箱注册 / 邮箱登录 / 验证码登录 / 头像"""
import base64
import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from config import CODE_LENGTH, CODE_RESEND_SECONDS, CODE_TTL_SECONDS, SMTP_MOCK
from database import get_db
from deps import get_current_user
from models import EmailCode, User
from schemas import LoginByCodeRequest, SendCodeRequest, UserLogin, UserOut, UserRegister
from security import create_token, hash_password, verify_password
from sender import send_code_email
from utils import fail, ok

router = APIRouter(prefix="/api/auth", tags=["认证"])


def _gen_code() -> str:
    """生成 6 位数字验证码"""
    return "".join(random.choices(string.digits, k=CODE_LENGTH))


def _user_out(user: User) -> dict:
    return UserOut.model_validate(user).model_dump(mode="json")


@router.post("/send-code")
def send_code(body: SendCodeRequest, db: Session = Depends(get_db)):
    """发送验证码：60 秒防重发，旧码作废，落库后发信"""
    recent = db.query(EmailCode).filter(
        EmailCode.email == body.email,
        EmailCode.purpose == body.purpose,
        EmailCode.created_at > datetime.utcnow() - timedelta(seconds=CODE_RESEND_SECONDS),
    ).first()
    if recent:
        wait = CODE_RESEND_SECONDS - int((datetime.utcnow() - recent.created_at).total_seconds())
        return fail(f"发送过于频繁，请{wait}秒后重试", 6)

    code = _gen_code()
    db.query(EmailCode).filter(
        EmailCode.email == body.email,
        EmailCode.purpose == body.purpose,
        EmailCode.used == False,  # noqa: E712
    ).update({EmailCode.used: True})
    db.add(EmailCode(email=body.email, code=code, purpose=body.purpose,
                     expires_at=datetime.utcnow() + timedelta(seconds=CODE_TTL_SECONDS), used=False))
    db.commit()

    if not send_code_email(body.email, code, body.purpose):
        return fail("邮件发送失败，请检查邮箱配置", 7)

    data = {"expires_in": CODE_TTL_SECONDS}
    if SMTP_MOCK:
        data["mock_code"] = code  # MOCK 模式返回验证码，便于无邮箱联调
    return ok(data)


@router.post("/register")
def register(body: UserRegister, db: Session = Depends(get_db)):
    """注册：校验验证码 → 邮箱唯一 → 创建用户 → 签发 JWT"""
    record = db.query(EmailCode).filter(
        EmailCode.email == body.email,
        EmailCode.code == body.code,
        EmailCode.purpose == "register",
        EmailCode.used == False,  # noqa: E712
    ).order_by(EmailCode.created_at.desc()).first()
    if not record:
        return fail("验证码错误", 2)
    if datetime.utcnow() > record.expires_at:
        return fail("验证码已过期", 2)

    if db.query(User).filter(User.email == body.email).first():
        return fail("该邮箱已注册", 3)

    record.used = True
    # 昵称默认取邮箱前缀，冲突时退回完整邮箱
    nickname = body.email.split("@")[0]
    if db.query(User).filter(User.username == nickname).first():
        nickname = body.email

    user = User(username=nickname, email=body.email,
                password_hash=hash_password(body.password), role="user", points=0)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.username, user.role)
    return ok({"access_token": token, "token_type": "bearer", "user": _user_out(user)})


@router.post("/login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    """邮箱 + 密码登录"""
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        return fail("该邮箱未注册", 4)
    if not verify_password(body.password, user.password_hash):
        return fail("密码错误", 5)

    token = create_token(user.id, user.username, user.role)
    return ok({"access_token": token, "token_type": "bearer", "user": _user_out(user)})


@router.post("/login-by-code")
def login_by_code(body: LoginByCodeRequest, db: Session = Depends(get_db)):
    """邮箱 + 验证码登录（免密）"""
    record = db.query(EmailCode).filter(
        EmailCode.email == body.email,
        EmailCode.code == body.code,
        EmailCode.purpose == "login",
        EmailCode.used == False,  # noqa: E712
    ).order_by(EmailCode.created_at.desc()).first()
    if not record:
        return fail("验证码错误", 2)
    if datetime.utcnow() > record.expires_at:
        return fail("验证码已过期", 2)

    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        return fail("该邮箱未注册", 4)

    record.used = True
    db.commit()

    token = create_token(user.id, user.username, user.role)
    return ok({"access_token": token, "token_type": "bearer", "user": _user_out(user)})


@router.post("/avatar")
def set_avatar(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """设置头像：上传图片，Base64 编码后存入数据库 User.avatar"""
    data = file.file.read()
    b64 = base64.b64encode(data).decode("ascii")
    mime = file.content_type or "image/jpeg"
    user.avatar = f"data:{mime};base64,{b64}"
    db.commit()
    db.refresh(user)
    return ok(_user_out(user))

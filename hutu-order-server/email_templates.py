"""验证码邮件模板：集中定义 purpose → 主题/场景/安全话术 映射。
sender.py 只负责 SMTP 发送，文案修改仅需动本文件。
新增场景（如 reset）：本文件 TEMPLATES 加一行 + schemas.py SendCodeRequest.purpose 正则加一项 + 前端枚举同步。
品牌与有效期统一从 config 注入（APP_BRAND / CODE_TTL_SECONDS），避免多处硬编码。
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import APP_BRAND, CODE_TTL_SECONDS

# purpose → 邮件模板；键需与 schemas.py 的 SendCodeRequest.purpose 正则保持一致
TEMPLATES = {
    "register": {
        "subject": "【{brand}】注册验证码 {code}",
        "scene": "您正在注册{brand}账号，本次验证码为：",
        "guard": "验证码 {ttl} 分钟内有效。请勿向任何人泄露，{brand}工作人员绝不会索要您的验证码。",
    },
    "login": {
        "subject": "【{brand}】登录验证码 {code}",
        "scene": "您正在登录{brand}账号，本次验证码为：",
        "guard": "验证码 {ttl} 分钟内有效。请勿向任何人泄露，{brand}工作人员绝不会索要您的验证码。",
    },
}


def _ttl_text() -> str:
    """有效期文案统一由配置 CODE_TTL_SECONDS 折算，避免正文两处硬编码。"""
    return f"{CODE_TTL_SECONDS // 60}"


def build_code_email(email: str, code: str, purpose: str, from_addr: str) -> MIMEMultipart:
    """按 purpose 取模板，构造标准验证码邮件（From/To/Subject + HTML 正文）。"""
    tpl = TEMPLATES.get(purpose, TEMPLATES["register"])
    subject = tpl["subject"].format(brand=APP_BRAND, code=code)
    scene = tpl["scene"].format(brand=APP_BRAND)
    guard = tpl["guard"].format(brand=APP_BRAND, ttl=_ttl_text())

    msg = MIMEMultipart()
    # From 带服务昵称（RFC2047 自动编码中文），收件箱将显示"校园点餐"而非裸账号
    msg["From"] = f"{APP_BRAND} <{from_addr}>"
    msg["To"] = email
    msg["Subject"] = subject

    html = f"""
    <div style="padding:32px;font-family:Arial,sans-serif;max-width:480px;margin:0 auto">
      <h2 style="color:#0637c9;margin:0 0 16px">{APP_BRAND} · 验证</h2>
      <p style="color:#555;margin:0 0 24px">{scene}</p>
      <div style="font-size:36px;font-weight:bold;color:#0637c9;letter-spacing:8px;
                  background:#f0f4ff;padding:20px;border-radius:12px;text-align:center;margin-bottom:24px">
        {code}
      </div>
      <p style="color:#999;font-size:14px;margin:0">{guard}</p>
    </div>
    """
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg

"""邮箱验证码发送：标准库 smtplib + email.mime，支持 QQ / 163 授权码（SMTP_SSL，465）。
SMTP_MOCK=True 时不发真邮件，验证码打印到日志。
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM,
    SMTP_SSL, SMTP_MOCK, CODE_TTL_SECONDS,
)

logger = logging.getLogger("email_auth")


def send_code_email(email: str, code: str, purpose: str = "register") -> bool:
    """发送验证码邮件，成功返回 True，失败返回 False。"""
    purpose_text = "注册" if purpose == "register" else "登录"

    if SMTP_MOCK:
        logger.info("[MOCK] 验证码 email=%s purpose=%s code=%s", email, purpose, code)
        return True

    if not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP 未配置 SMTP_USER / SMTP_PASSWORD")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = email
        msg["Subject"] = f"邮箱{purpose_text}验证码"

        html = f"""
        <div style="padding:32px;font-family:Arial,sans-serif;max-width:480px;margin:0 auto">
          <h2 style="color:#0637c9;margin:0 0 16px">邮箱{purpose_text}验证</h2>
          <p style="color:#555;margin:0 0 24px">您的验证码为：</p>
          <div style="font-size:36px;font-weight:bold;color:#0637c9;letter-spacing:8px;
                      background:#f0f4ff;padding:20px;border-radius:12px;text-align:center;margin-bottom:24px">
            {code}
          </div>
          <p style="color:#999;font-size:14px;margin:0">
            验证码 {CODE_TTL_SECONDS // 60} 分钟内有效，请勿泄露给他人。
          </p>
        </div>
        """
        msg.attach(MIMEText(html, "html", "utf-8"))

        if SMTP_SSL:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.starttls()

        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, email, msg.as_string())
        server.quit()
        logger.info("验证码邮件已发送 email=%s purpose=%s", email, purpose)
        return True
    except Exception as e:
        logger.error("邮件发送失败 email=%s error=%s", email, str(e))
        return False

"""邮箱验证码发送：从 email_templates 取模板，仅负责 SMTP 连接与投递。
SMTP_MOCK=True 时不发真邮件，验证码打印到日志。
"""
import logging
import smtplib

from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM,
    SMTP_SSL, SMTP_MOCK,
)
from email_templates import build_code_email

logger = logging.getLogger("email_auth")


def send_code_email(email: str, code: str, purpose: str = "register") -> bool:
    """发送验证码邮件，成功返回 True，失败返回 False。"""
    if SMTP_MOCK:
        logger.info("[MOCK] 验证码 email=%s purpose=%s code=%s", email, purpose, code)
        return True

    if not SMTP_USER or not SMTP_PASSWORD:
        logger.error("SMTP 未配置 SMTP_USER / SMTP_PASSWORD")
        return False

    try:
        msg = build_code_email(email, code, purpose, SMTP_FROM)

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

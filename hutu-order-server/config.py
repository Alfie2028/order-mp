"""全局配置：安全密钥、BufPay、数据库连接"""
import os

# ---- 安全 ----
JWT_SECRET = os.getenv("JWT_SECRET", "campus-order-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

# ---- BufPay 聚合支付（免签模式，需安卓手机挂机监控到账）----
# aid / secret 在 BufPay 后台「应用配置」页查看；留空时支付自动走模拟
BUFPAY_AID = os.getenv("BUFPAY_AID", "")
BUFPAY_SECRET = os.getenv("BUFPAY_SECRET", "")
BUFPAY_PAY_URL = "https://bufpay.com/api/pay/{aid}"
BUFPAY_QUERY_URL = "https://bufpay.com/api/query/{aoid}"

# ---- 邮箱验证码（SMTP 发信）----
# 默认内置一个 QQ 邮箱授权码，直接 uvicorn 即可真发邮件；SMTP_MOCK=True 时打印验证码不发真邮件
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "2127912648@qq.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "bbuduythwrjwjgdf")  # 授权码，非登录密码
SMTP_FROM = os.getenv("SMTP_FROM", "") or SMTP_USER
SMTP_SSL = os.getenv("SMTP_SSL", "True").lower() in ("true", "1", "yes")
SMTP_MOCK = os.getenv("SMTP_MOCK", "False").lower() in ("true", "1", "yes")

CODE_TTL_SECONDS = int(os.getenv("CODE_TTL_SECONDS", "300"))       # 验证码有效期（秒）
CODE_RESEND_SECONDS = int(os.getenv("CODE_RESEND_SECONDS", "60"))  # 重发间隔（秒）
CODE_LENGTH = 6

# ---- 数据库 ----
DATABASE_URL = "sqlite:///./campus_order.db"

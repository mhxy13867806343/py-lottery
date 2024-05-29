from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from tool.emailTools import emailTools
import secrets
conf = ConnectionConfig(
    MAIL_USERNAME = emailTools.get("to_email"),
    MAIL_PASSWORD = emailTools.get("to_main_password"),
    MAIL_FROM = emailTools.get("to_email"),
    MAIL_PORT = emailTools.get("to_serverPort"),
    MAIL_SERVER =emailTools.get("to_serverHost"),
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

verification_data = {}
async def sendBindEmail(email:str=""):
    # 生成一个随机验证码
    code = secrets.token_urlsafe(8)
    # 存储验证码和邮箱
    verification_data[email] = code

    message = MessageSchema(
        subject="Verify your email address",
        recipients=[email],
        body=f"Please verify your email by using this code: {code}",
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {
        "message":message,
        "verification_data":verification_data,
        "code":code
    }

async def getVerifyEmail(email:str="", code: str = ""):
    if email in verification_data and verification_data[email] == code:
        return True
    return False
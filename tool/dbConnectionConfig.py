from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import status
from tool.emailTools import emailTools
import secrets
from datetime import datetime, timedelta

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
        subject="验证您的邮箱地址",
        recipients=[email],
        body=f"请查询您的邮箱中的验证码: {code}，有效期为5分钟，请尽快验证。",
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
    if email not in verification_data:
        return {
            "code":-800,
            "message":"验证码不存在"
        }
        # 获取验证码数据
    code_data = verification_data[email]
    code_timestamp = code_data['timestamp']

    # 检查验证码是否在5分钟内
    if datetime.now() - code_timestamp > timedelta(minutes=5):
        # 如果超时，则删除验证码数据
        del verification_data[email]
        return {
            "code":-801,
            "message":"验证码已过期"
        }

    # 检查验证码是否正确
    if code_data['code'] == code:
        # 如果验证成功，则删除验证码数据
        del verification_data[email]
        return {
            "code":status.HTTP_200_OK,
            "message":"验证成功"
        }
    return {
        "code":-802,
        "message":"验证码错误"
    }

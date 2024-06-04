
from fastapi import status
from datetime import datetime, timedelta
import secrets

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from tool.emailTools import emailTools
verification_data = {}
import random
import string

def generate_random_code():
    all_chars = string.ascii_letters + string.digits  # 包含所有字母和数字
    code = ''.join(random.choice(all_chars) for _ in range(6))
    return code
def sendBindEmail(from_email: str = ""):
    now = datetime.now()

    # 检查是否已经发送过验证码，并且在5分钟内
    if from_email in verification_data:
        last_sent = verification_data[from_email]['timestamp']
        if (now - last_sent) < timedelta(minutes=5):
            return {
                "code": -80008,
                "result": {},
                "message": "验证码已发送到您的邮箱中去了，请5分钟后再试"
            }


    # 生成一个随机验证码
    code = generate_random_code()

    # 更新存储验证码和时间戳
    verification_data[from_email] = {
        "code": code,
        "timestamp": now
    }

    # 创建邮件内容
    message = MIMEText(f"\n您的验证码是: {code}", 'plain', 'utf-8')
    to_email = emailTools.get('to_email')
    server_host = emailTools.get('to_serverHost')
    server_port = emailTools.get('to_serverPort')
    main_password = emailTools.get('to_main_password')

    # 设置邮件头部信息
    message['To'] = formataddr(('Recipient Name', to_email))
    message['From'] = formataddr(('Current User', from_email))
    message['Subject'] = "发送您的验证码"

    # 连接SMTP服务器并发送邮件
    try:
        server = smtplib.SMTP_SSL(server_host, server_port)
        server.login(from_email, main_password)
        server.set_debuglevel(1)  # 启用调试输出
        server.sendmail(from_email, [to_email], message.as_string())
        response = {
            "code": status.HTTP_200_OK,
            "result": {},
            "message": "发送成功"
        }
    except smtplib.SMTPException as e:
        print("邮件发送失败:", e)
        response = {
            "code": -800,
            "result": {},
            "message": "发送失败"
        }
    finally:
        server.quit()
        return response

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

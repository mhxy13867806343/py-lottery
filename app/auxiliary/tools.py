import smtplib
import email.utils
from email.mime.text import MIMEText
isSend=True
sbError=False
import hashlib
import random
import datetime
from tool.emailTools import emailTools

def generateEmailId(email_address: str) -> str:
    # 获取当前日期，格式为YYYYMMDD
    current_date = datetime.datetime.now().strftime("%Y%m%d")

    # 对邮箱地址进行MD5加密，并取前22位
    md5_hash = hashlib.md5(email_address.encode()).hexdigest()[:22]

    # 随机生成包含26个字母大小写的字符串，长度为6位
    random_string = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', k=6))

    # 组合所有部分，确保总长度为36位
    email_id = current_date + md5_hash + random_string

    return email_id

def sendEmail(title:str="反馈网站内容", content:str="测试用户数据进行反馈相关内容的测试",from_email:str=None):
    message = MIMEText(content)
    to_email:str = emailTools.get('to_email')
    message['To'] = email.utils.formataddr(('hooks', to_email))
    message['From'] = email.utils.formataddr(('当前用户', from_email))
    message['Subject'] = title
    server = smtplib.SMTP_SSL(emailTools.get('to_serverHost'), emailTools.get('to_serverPort'))
    server.login(from_email, emailTools.get('to_main_password'))
    server.set_debuglevel(True)
    try:
        isSend = True
        server.sendmail(from_email, [to_email], msg=message.as_string())
    except smtplib.SMTPServerDisconnected as e:
        sbError = True
    finally:
        isSend=False
        server.quit()

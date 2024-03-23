import smtplib
import email.utils
from email.mime.text import MIMEText
isSend=True
def sendEmail(title:str="反馈网站内容", content:str="测试用户数据进行反馈相关内容的测试",from_email:str=None):
    message = MIMEText(content)
    to_email:str =  '869710179@qq.com'
    message['To'] = email.utils.formataddr(('hooks', to_email))
    message['From'] = email.utils.formataddr(('当前用户', from_email))
    message['Subject'] = title
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(from_email, 'sviyibdxlqqrbaie')
    server.set_debuglevel(True)
    try:
        isSend = True
        server.sendmail(from_email, [to_email], msg=message.as_string())
    finally:
        isSend=False
        server.quit()

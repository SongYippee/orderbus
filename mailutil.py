# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

def send_mail(receiver,message):
    mail_server = "smtp.163.com"  # mail server
    mail_user = "xxxxxx@163.com"  # mail user account
    mail_code = "xxxxxx"  # mail authorization code to login use
    sender = 'xxxxxx@163.com' # your mail account
    mail_body = message
    message = MIMEText(mail_body, 'html', 'utf-8')
    subject = '班车抢票成功'
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = sender
    message['To'] = receiver

    server = smtplib.SMTP_SSL()
    server.connect(mail_server,465)
    server.login(mail_user, mail_code)
    server.sendmail(sender, receiver, message.as_string())
    server.close()
    print "邮件发送成功"


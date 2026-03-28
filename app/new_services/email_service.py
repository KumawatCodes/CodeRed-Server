import smtplib
from email.message import EmailMessage

def send_otp_email(email: str, otp: str):
    msg = EmailMessage()
    msg.set_content(f"Your OTP is {otp}")
    msg['Subject'] = "Verify your email"
    msg['From'] = "your@gmail.com"
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("codeforgebattle@gmail.com", "qzir wzfm akcq kcee")
        smtp.send_message(msg)
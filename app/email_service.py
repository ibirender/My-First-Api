# app/email.py

import smtplib,os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mailtrap Credentials
MAIL_HOST = os.getenv("MAIL_HOST")
MAIL_PORT = int(os.getenv("MAIL_PORT"))
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASS")


def send_reset_email(to_email: str, otp: str):

    subject = "🔐 Your Password Reset OTP"

    html_content = f"""
    <h2>Password Reset OTP</h2>
    <p>Your OTP is:</p>
    <h1>{otp}</h1>
    <p>This OTP expires in 10 minutes.</p>
    """

    text_content = f"""
    Password Reset OTP
    Your OTP is: {otp}
    """

    # Create message
    msg = MIMEMultipart("alternative")
    msg["From"] = MAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # 🔥 THIS PART GOES HERE
    try:
        with smtplib.SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USER, MAIL_PASS)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email error:", e)
        return False
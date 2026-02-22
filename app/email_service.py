# app/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Mailtrap Credentials
MAILTRAP_HOST = "sandbox.smtp.mailtrap.io"
MAILTRAP_PORT = 2525   # Recommended for Mailtrap
MAILTRAP_USER = "249c809f570d1e"
MAILTRAP_PASS = "a4bcdb214657ed"


def send_reset_email(to_email: str, otp: str):

    subject = "🔐 Your Password Reset OTP"

    # Create message container
    msg = MIMEMultipart("alternative")
    msg["From"] = MAILTRAP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Plain text version
    text_content = f"""
    Password Reset OTP

    Your OTP is: {otp}

    It expires in 30 minutes.
    """

    # HTML version
    html_content = f"""
    <html>
        <body style="font-family: Arial;">
            <h2>Password Reset OTP</h2>
            <p>Your OTP code is:</p>
            <h1 style="letter-spacing: 5px;">{otp}</h1>
            <p>This OTP will expire in <strong>30 minutes</strong>.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
    </html>
    """

    # Attach both parts
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        print("Connecting to Mailtrap...")

        server = smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT)
        server.starttls()  # STARTTLS required
        server.login(MAILTRAP_USER, MAILTRAP_PASS)

        server.sendmail(MAILTRAP_USER, to_email, msg.as_string())
        server.quit()

        print("✅ Mail sent successfully")

    except Exception as e:
        print("❌ MAIL ERROR:", e)
# app/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Mailtrap credentials from .env
MAILTRAP_HOST = os.getenv("MAILTRAP_HOST", "sandbox.smtp.mailtrap.io")
MAILTRAP_PORT = int(os.getenv("MAILTRAP_PORT", 2525))
MAILTRAP_USER = os.getenv("MAILTRAP_USER", "")
MAILTRAP_PASS = os.getenv("MAILTRAP_PASS", "")

def send_reset_email(to_email: str, reset_token: str):
    """
    Mailtrap ke through password reset email bhejo
    """
    # Frontend URL (localhost ya jo bhi ho)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    # Email content
    subject = "🔐 Password Reset Request"
    
    # HTML email template
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
                .button {{
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 12px 24px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>Click the button below to reset your password:</p>
                
                <a href="{reset_link}" class="button">Reset Password</a>
                
                <p>Or copy this link:</p>
                <p><code>{reset_link}</code></p>
                
                <p>This link will expire in <strong>1 hour</strong>.</p>
                
                <p>If you didn't request this, please ignore this email.</p>
            </div>
        </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Password Reset Request
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    """
    
    # Create message
    msg = MIMEMultipart("alternative")
    msg["From"] = "noreply@yourapp.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    
    # Attach both versions
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        # Mailtrap se connect karo
        print(f"📧 Sending email to {to_email}...")
        
        with smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT) as server:
            server.starttls()  # TLS start karo
            server.login(MAILTRAP_USER, MAILTRAP_PASS)
            server.send_message(msg)
        
        print(f"✅ Email sent successfully!")
        print(f"📬 Check your Mailtrap inbox!")
        print(f"🔗 Reset link: {reset_link}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

# Test function - direct run karne ke liye
if __name__ == "__main__":
    # Test email
    test_email = "test@example.com"
    test_token = "test-token-123456"
    
    print("🚀 Testing email send...")
    send_reset_email(test_email, test_token)
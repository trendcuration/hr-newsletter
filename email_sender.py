import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENTS


def send_newsletter(subject: str, html_content: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"HR Weekly Brief <{GMAIL_USER}>"
    msg["To"] = ", ".join(RECIPIENTS)

    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, RECIPIENTS, msg.as_string())
        print(f"메일 발송 완료 → {', '.join(RECIPIENTS)}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Gmail 인증 오류: 앱 비밀번호를 확인하세요.")
        raise
    except Exception as e:
        print(f"메일 발송 오류: {e}")
        raise

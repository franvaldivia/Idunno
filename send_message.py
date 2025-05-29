import os
from datetime import datetime,timedelta
from email.message import EmailMessage
import ssl
import smtplib

def enviar_email():
    email_sender = 'valdiviafran2025@gmail.com'
    password = 'isay ldci vtab oucn'
    email_reciver = 'valdiviafran2025@gmail.com'
    subject = "¡¡¡¡¡FALLO MAQUINA!!!!!!"
    body = "Estan fallando los regalos\n\n"
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_reciver
    em["Subject"] = subject
    em.set_content(body)
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email_reciver, em.as_string())

    return True
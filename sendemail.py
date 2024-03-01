import smtplib
from email.message import EmailMessage
import mimetypes


def send_email_with_attachment(
    subject="New SpreadSheet",
    body="Here you go dummy",
    attachment_path="DataFrames\Predictions_for_today.xlsx",
):

    receiver = "mikesyanks02@icloud.com"
    sender = "michael.scoleri@outlook.com"
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(body)

    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    mime_subtype = "sheet"

    with open(attachment_path, "rb") as file:
        file_content = file.read()
        msg.add_attachment(
            file_content,
            maintype=mime_type,
            subtype=mime_subtype,
            filename=attachment_path,
        )

        # Log in to your email server and send the email
    print("Attempting to connect to SMTP server...")
    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    print("Connected to SMTP server. Attempting to log in...")
    smtp.login("michael.scoleri@outlook.com", "Has2sister$")
    print("Logged in. Preparing to send email...")
    smtp.sendmail(from_addr=sender, to_addrs=receiver, msg=msg.as_string())
    print("Email Sent!")

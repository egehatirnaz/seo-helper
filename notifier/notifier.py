import smtplib, ssl, env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Notifier:
    def __init__(self):
        self.sender_email = env.SMTP_EMAIL
        self.password = env.SMTP_PASSWORD
        self.smtp_server = env.SMTP_SERVER
        self.port = env.SMTP_PORT  # For starttls


    def sendNotification(self, receiver_email):
        message = MIMEMultipart("alternative")
        message["Subject"] = "Seo Helper - Notification E-Mail"
        message["From"] = self.sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        text = """\
        This is a HTML message and it does not support plain-text at the moment!"""

        html = open("WeeklyReport.html")

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html.read(), "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(env.SMTP_SERVER, env.SMTP_PORT, context=context) as server:
            server.login(env.SMTP_EMAIL, env.SMTP_PASSWORD)
            server.sendmail(
                env.SMTP_EMAIL, receiver_email, message.as_string()
            )

    def main(self):
        self.sendNotification("egehatirnaz@gmail.com")


if __name__ == '__main__':
    n = Notifier()
    n.main()

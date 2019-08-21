import smtplib, ssl, env
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Notifier:
    def __init__(self):
        self.sender_email = env.SMTP_EMAIL
        self.password = env.SMTP_PASSWORD
        self.smtp_server = env.SMTP_SERVER
        self.port = env.SMTP_PORT  # For starttls

    def send_notification(self, receiver_email, html_message):
        message = MIMEMultipart("alternative")
        message["Subject"] = "Seo Helper - Notification E-Mail"
        message["From"] = self.sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        text = """\
        This is a HTML message and it does not support plain-text at the moment!"""

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html_message, "html")

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

    def notify(self, user_email, user_name, urls_error_list):
        message = open("notifier/mail-template.html").read()
        message = message.replace("{{user_name}}", user_name)

        urls_and_errors_string = ""

        # urls_error_list = [{url#1: [[error_name, err_desc], [error_name, err_desc]]},
        #                    {url#2: [[error_name, err_desc], [error_name, err_desc]]}]
        for analysis_url in urls_error_list:
            web_err_list = list(analysis_url.items())[0]
            website_url, err_list = web_err_list[0], web_err_list[1]
            analysis_url_result_string = """
                <h3>{0}:</h3>
                <table class="result-table" role="presentation"
                       style="border-style: solid; border-width:1px; padding:10px 5px;">
                    <tbody>
                    <tr>
                        <td>
                            <b>Found Errors</b>
                        </td>
                        <td>
                            <b>Description</b>
                        </td>
                    </tr>""".format(website_url)
            for err in err_list:
                error_name = err[0]
                error_description = err[1]
                analysis_url_result_string += "<tr><td>" + error_name + "</td><td>" + error_description + "</td></tr>"
            analysis_url_result_string += "</tbody></table><br><br>"
            urls_and_errors_string += analysis_url_result_string
        message = message.replace("{{urls_and_errors}}", urls_and_errors_string)

        try:
            self.send_notification(user_email, message)
            return "Notification sent successfully!"
        except Exception as e:
            return e

    def main(self):
        urls_error_list = [{"url#1": [["error_name", "err_desc"],
                                      ["error_name", "err_desc"]]},
                           {"url#2": [["error_name", "err_desc"],
                                      ["error_name", "err_desc"]]}]

        self.notify("egehatirnaz@gmail.com", "Ege Hatırnaz", urls_error_list)


if __name__ == '__main__':
    n = Notifier()
    n.main()

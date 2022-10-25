from imaplib import IMAP4_SSL
import email
from smtp import User, get_password, KEY


# TODO: Figure out how to deal with files


class EmailReader(IMAP4_SSL):
    ignore_list = [
        '"The NordVPN team" <support@nordvpn.com>',
        "LinkedIn <messages-noreply@linkedin.com>",
    ]

    def __init__(self, host, port_number) -> None:
        super().__init__(host, port_number)
        self.host = host
        self.port = port_number

    def log_in(self, user: User) -> None:
        """
        Logs in to the server
        """
        self.login(user.email, user.password)

    def get_emails(self, folder: str) -> list:
        """
        Gets all the emails from the specified folder
        """
        emails = []
        self.select(folder)
        _, msg_nums = self.search(None, "ALL")
        revered_mail = sorted(msg_nums[0].split(), key=int, reverse=True)
        for num in revered_mail[0:10]:
            mail = {}
            _, data = self.fetch(num, "(RFC822)")
            message = email.message_from_bytes(data[0][1])

            if message.get("From") in self.ignore_list:
                continue

            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.as_string()

            mail.update(
                {
                    "message number": num,
                    "subject": message.get("Subject"),
                    "from": message.get("from"),
                    "to": message.get("to"),
                    "date": message.get("date"),
                    "BCC": message.get("BCC"),
                    "body": body,
                }
            )
            emails.append(mail)
        return emails

    def add_to_ignore_list(self, email_address) -> None:
        """
        Adds an email to the ignore list
        will create a file to write the emails to
        """
        ...

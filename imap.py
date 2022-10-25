from imaplib import IMAP4_SSL
import email
from smtp import User


class EmailReader(IMAP4_SSL):
    def __init__(self, host, port_number, ignore_list=None) -> None:
        super().__init__(host, port_number)
        self.host = host
        self.port = port_number
        if ignore_list is None:
            self.ignore_list = []
    
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

        for num in reversed(msg_nums[0].split()):
            mail = {}
            _, data = self.fetch(num, "(RFC822)")
            message = email.message_from_bytes(data[0][1])

            if message.get("From") in self.ignore_list:
                continue
            
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")
                elif part.get_content_type() == "text/html":
                   body = part.get_payload(decode=True).decode("utf-8")
                elif part.get_content_type() == "multipart/alternative":
                    continue
                else:
                    mail["attachment"] = part.get_payload(decode=True)
                    mail["attachment_name"] = part.get_filename()

            mail.update({
                "message number": num,
                "subject": message.get("Subject"),
                "from": message.get("from"),
                "to": message.get("to"),
                "date": message.get("date"),
                "BCC": message.get("BCC"),
                "body": body
            })

            emails.append(mail)
        return emails
    
    def add_to_ignore_list(self, email_address) -> None:
        """
        Adds an email to the ignore list
        """
        self.ignore_list.append(email_address)



        


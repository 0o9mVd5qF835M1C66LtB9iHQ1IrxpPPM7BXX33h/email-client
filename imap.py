from imaplib import IMAP4_SSL
import email
# Just need this import for testing will likely remove later
from smtp import User, get_password, KEY, FROM_ADDR, PORT


# TODO: Figure out how to deal with files

class EmailReader(IMAP4_SSL):
    ignore_list = []

    def __init__(self, host: str, port_number: int) -> None:
        super().__init__(host, port_number)
        self.host = host
        self.port = port_number

    def log_in(self, user: User) -> None:
        """
        Logs in to the server
        """
        self.login(user.email, user.password)

    def get_emails(self, folder: str, amount=10) -> list:
        """
        Gets first N emails from the specified folder
        """
        emails = []
        self.select(folder)
        _, msg_nums = self.search(None, "ALL")
        reversed_mail = sorted(msg_nums[0].split(), key=int, reverse=True)
        for num in reversed_mail[0:amount]:
            mail = {}
            _, data = self.fetch(num, "(RFC822)")
            message = email.message_from_bytes(data[0][1])

            # Cleaning up email address to check against ignore list
            email_addr = message.get("From").split(" ")[-1]

            email_addr = email_addr.replace("<", "").replace(">", "")

            if email_addr in self.ignore_list:
                continue

            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8")
                    # body = part.as_string()

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
    

    def add_to_ignore_list(self, email_address: str) -> None:
        """
        Adds an email to the ignore list
        """
        with open("ignore_list.txt", "a") as f:
            f.write(email_address + "\n")
        
    def ignore_list_setter(self) -> None:
        """
        Sets the ignore list to the emails in the file
        Needs to be called on instance of class
        """
        with open("ignore_list.txt", "r") as f:
            self.ignore_list = f.read().splitlines()


def main():
    password = get_password("credentials.txt", KEY)
    user = User(FROM_ADDR, password)
    server = EmailReader("outlook.office365.com", 993)
    server.log_in(user)
    server.ignore_list_setter()
    emails = server.get_emails("INBOX")
    for email in emails:
        print(email["from"])
        print(email["subject"])
        print(email["body"])
        print()

if __name__ == "__main__":
    main()
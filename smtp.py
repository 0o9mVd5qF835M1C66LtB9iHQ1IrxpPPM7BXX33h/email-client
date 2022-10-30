import re
from smtplib import SMTP
from cryptography.fernet import Fernet
from dotenv import dotenv_values
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders


CONFIG = dotenv_values(".env")
KEY = CONFIG["KEY"]
FROM_ADDR = str(CONFIG["EMAIL"])
PORT = 587
SMTP_SERVER = CONFIG["SMTP_SERVER"]
IMAP_SERVER = CONFIG["IMAP_SERVER"]
IMAP_PORT = CONFIG["IMAP_PORT"]


class Server(SMTP):
    connected = False
    def __init__(self, host: str, port_number: int) -> None:
        super().__init__(host, port_number)
        self.host = host
        self.port = port_number

    def __str__(self) -> str:
        return f"{self.host} server"

    def make_connection(self, user) -> None:
        """
        Makes connection to the server
        """
        self.starttls()
        self.ehlo()
        self.login(user.email, user.password)
        self.connected = True

    def send_email(self, from_address: str, to_address: str, message: MIMEMultipart) -> bool:
        """
        Sends an email
        """
        for address in [from_address, to_address]:
            if not self.validate_email(address):
                return False
        
        # We need to send the mail here...
        if self.connected:
            rejections = self.sendmail(from_address, to_address, message.as_string())
            self.quit()
            self.connected = False
            # Sendmail returns a dictionary of rejected addresses
            if rejections:
                return False
            
            return True
        return False

    @classmethod
    def validate_email(self, email_address) -> bool:
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return True if re.fullmatch(regex, email_address) else False


class User:
    def __init__(self, email, password) -> None:
        self._email = email
        self._password = password

    def __str__(self) -> str:
        return f"User: {self.email}"

    @property
    def email(self) -> str:
        return self._email

    @property
    def password(self) -> str:
        return self._password
    
    def construct_email(self, to_address, body, subject) -> MIMEMultipart:
        """
        Constructs an email
        For now we will only send text emails
        Later we will add attachment perhaps an email class will be needed
        """
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = to_address
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        return message


def get_password(file: str, key: str) -> str:
    """
    Returns decrypted password
    """
    f = open(file)
    password = f.readline().strip()
    f.close()
    fernet = Fernet(key.encode())
    password = fernet.decrypt(password.encode()).decode("utf-8")
    return password

from tkinter import *
from typing import Any
from smtp import (
    Server,
    User,
    get_password,
    CONFIG,
)
from imap import EmailReader


class LogInFrame:
    def __init__(self, master: Any) -> None:
        self.master = master
        self.frame = Frame(self.master, width=800, height=800, padx=80, pady=80)
        self.username = StringVar()
        self.password = StringVar()

        # Labels
        self.username_label = Label(self.frame, text="Username", padx=10, pady=10).grid(
            row=0, column=0
        )
        self.password_label = Label(self.frame, text="Password", padx=10, pady=10).grid(
            row=1, column=0
        )

        # Entries
        self.username_entry = Entry(
            self.frame, textvariable=self.username, width=28
        ).grid(row=0, column=1)
        self.password_entry = Entry(
            self.frame, textvariable=self.password, show="*", width=28
        ).grid(row=1, column=1)

        # Buttons
        self.login_button = Button(
            self.frame, text="Login", command=self.login_check
        ).grid(row=2, column=0, columnspan=2, pady=10)

        self.frame.grid()

    def login_check(self):
        username = self.username.get()
        password = self.password.get()

        password_check = get_password("credentials.txt", CONFIG["KEY"])
        email_check = CONFIG["EMAIL"]

        if password == password_check and username == email_check:
            self.frame.destroy()
            DecisionsFrame(self.master)
        else:
            PopUp(self.master, "Incorrect username or password")


class ComposeEmailFrame:
    def __init__(self, master: Any) -> None:
        self.master = master
        self.frame = Frame(self.master, width=800, height=800, padx=40, pady=40)
        self.frame.grid()
        self.to_address = StringVar()
        self.subject = StringVar()
        self.body = StringVar()

        # Labels
        self.to_address_label = Label(self.frame, text="To:").grid(
            row=0, column=0, padx=10, pady=10
        )
        self.subject_label = Label(self.frame, text="Subject:").grid(
            row=1, column=0, padx=10, pady=10
        )
        self.body_label = Label(self.frame, text="Body:").grid(row=2, column=0)

        # Entries
        self.to_address_entry = Entry(
            self.frame, textvariable=self.to_address, width=40
        ).grid(row=0, column=1)
        self.subject_entry = Entry(
            self.frame, textvariable=self.subject, width=40
        ).grid(row=1, column=1)
        self.body_text = Text(self.frame, width=50, height=10)
        self.body_text.grid(row=2, column=1)

        # Buttons
        self.send_button = Button(
            self.frame, text="Send", command=self.send_email
        ).grid(row=3, column=0, columnspan=2, pady=10)
        self.log_out_button = Button(
            self.frame, text="Log Out", command=self.log_out
        ).grid(row=4, column=0, columnspan=2, pady=10)
        self.back_button = Button(
            self.frame, text="Back", command=self.back
        ).grid(row=5, column=0, columnspan=2, pady=10)

    def send_email(self):
        to_addr = self.to_address.get()
        subject = self.subject.get()
        body = self.body.get()

        if "" in (to_addr, body):
            PopUp(self.master, "Please fill out all fields")
            return

        if not Server.validate_email(to_addr):
            PopUp(self.master, "Error Invalid email address")
            return

        user = User(CONFIG["EMAIL"], get_password("credentials.txt", CONFIG["KEY"]))
        server = Server(CONFIG["SMTP_SERVER"], CONFIG["SMTP_PORT"])
        server.make_connection(user)

        message = user.construct_email(to_addr, body, subject)
        sent = server.send_email(user.email, to_addr, message)
        if sent:
            PopUp(self.master, "Email sent successfully")
        else:
            PopUp(self.master, "Error sending email")
        self.clear_fields()

    def clear_fields(self):
        self.to_address.set("")
        self.subject.set("")
        self.body_text.delete(1.0, END)

    def log_out(self):
        self.frame.destroy()
        LogInFrame(self.master)
    
    def back(self):
        self.frame.destroy()
        DecisionsFrame(self.master)


class PopUp:
    def __init__(self, master: Any, message: str) -> None:
        self.master = master
        self.window = Toplevel(self.master)
        self.window.title("Error")
        self.window.geometry("300x100")
        self.window.resizable(False, False)
        self.window.grab_set()
        self.window.focus_set()
        self.window.transient(self.master)
        # Make window center of main window
        self.window.geometry(
            "+%d+%d" % (self.master.winfo_rootx() + 50, self.master.winfo_rooty() + 50)
        )

        self.message = message
        self.message_label = Label(self.window, text=self.message).pack(
            padx=10, pady=10
        )
        self.ok_button = Button(
            self.window, text="OK", command=self.window.destroy
        ).pack(pady=10)


class MailReadingFrame:
    def __init__(self, master: Any) -> None:
        self.master = master
        self.frame = Frame(self.master, width=800, height=800, padx=40, pady=40)
        self.frame.grid()
        self.emails = imap.get_emails("INBOX")
        self.emails_list = Listbox(self.frame, width=100, height=20)
        self.emails_list.grid(row=0, column=0, columnspan=2)
        self.read_button = Button(
            self.frame, text="Read", command=self.read_email
        ).grid(row=1, column=0, pady=10)
        self.back_button = Button(self.frame, text="Back", command=self.back).grid(
            row=1, column=1, pady=10
        )
        self.populate_list()

    def populate_list(self):
        for email in self.emails:
            list_item = f"{email['from']} - {email['subject']}"
            self.emails_list.insert(END, list_item)

    def read_email(self):
        selection = self.emails_list.curselection()
        if selection:
            email = self.emails[selection[0]]
            self.frame.destroy()
            EmailFrame(self.master, email)

    def back(self):
        self.frame.destroy()
        DecisionsFrame(self.master)


class EmailFrame:
    def __init__(self, master: Any, email) -> None:
        self.master = master
        self.frame = Frame(self.master, width=800, height=800, padx=40, pady=40)
        self.frame.grid()
        self.email = email
        self.email_text = Text(self.frame, width=100, height=20)
        self.email_text.grid(row=0, column=0, columnspan=2)
        self.back_button = Button(self.frame, text="Back", command=self.back).grid(
            row=1, column=0, pady=10
        )
        self.populate_text()

    def populate_text(self):
        from_addr = self.email.get("from")
        subject = self.email.get("subject")
        body = self.email.get("body")
        email_text = f"From: {from_addr}\nSubject: {subject}\n\n{body}"
        self.email_text.insert(END, email_text)

    def back(self):
        self.frame.destroy()
        MailReadingFrame(self.master)


class DecisionsFrame:
    # Frame for user to decide whether to read or compose emails
    def __init__(self, master: Any) -> None:
        self.master = master
        self.frame = Frame(self.master, width=800, height=800, padx=40, pady=40)
        self.frame.grid()
        self.read_button = Button(
            self.frame, text="Read Emails", command=self.read_emails
        ).grid(row=0, column=0, pady=10)
        self.compose_button = Button(
            self.frame, text="Compose Email", command=self.compose_email
        ).grid(row=0, column=1, pady=10)
        self.log_out_button = Button(
            self.frame, text="Log Out", command=self.log_out
        ).grid(row=1, column=0, columnspan=2, pady=10)
    
    def read_emails(self):
        self.frame.destroy()
        MailReadingFrame(self.master)
    
    def compose_email(self):
        self.frame.destroy()
        ComposeEmailFrame(self.master)
    
    def log_out(self):
        self.frame.destroy()
        LogInFrame(self.master)
    

class App:
    def __init__(self, master: Any) -> None:
        self.master = master
        self.master.title("Email Client")
        LogInFrame(self.master)


if __name__ == "__main__":
    imap = EmailReader(CONFIG["IMAP_SERVER"], CONFIG["IMAP_PORT"])
    imap.log_in(User(CONFIG["EMAIL"], get_password("credentials.txt", CONFIG["KEY"])))
    imap.ignore_list_setter()
    root = Tk()
    root.title("Email Client")
    root.resizable(False, False)
    App(root)
    root.mainloop()

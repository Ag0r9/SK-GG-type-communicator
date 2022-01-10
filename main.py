import sys
import socket
from threading import Thread

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication


class WelcomePage(QDialog):
    def __init__(self):
        super(WelcomePage, self).__init__()
        loadUi('UI/welcome_page.ui', self)
        self.login.clicked.connect(self.gotologin)
        self.signup.clicked.connect(self.gotoregistration)

    def gotologin(self):
        widget.setCurrentIndex(1)

    def gotoregistration(self):
        widget.setCurrentIndex(2)


class LoginPage(QDialog):
    def __init__(self):
        super(LoginPage, self).__init__()
        loadUi('UI/login_page.ui', self)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.login_function)

    def login_function(self):
        user = self.username_field.text()
        password = self.password_field.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText('Please input all fields!')
        elif ' ' in user or ' ' in password:
            self.error.setText('Write correct password and username!')
        else:
            send_message('LOGIN', f'{user} {password}')


class RegistrationPage(QDialog):
    def __init__(self):
        super(RegistrationPage, self).__init__()
        loadUi('UI/signup_page.ui', self)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_confirm_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signup_function)

    def signup_function(self):
        user = self.username_field.text()
        password = self.password_field.text()
        password_confirm = self.password_confirm_field.text()

        if len(user) == 0 or len(password) == 0 or len(password_confirm) == 0:
            self.error.setText('Please input all fields!')
        elif password != password_confirm:
            self.error.setText('You wrote two different passwords!')
        else:
            send_message('SIGNUP', f'{user} {password}')


class MenuPage(QDialog):
    def __init__(self):
        super(MenuPage, self).__init__()
        loadUi('UI/menu_page.ui', self)


if __name__ == '__main__':
    gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gniazdo.connect(("localhost", 8021))

    def send_message(header, content):
        """
        :example:
        send_message("SIGNUP", "user password")
        send_message("LOGIN", "user password")
        """
        message = f'\t{header}\t{content}\t'
        for i in message:
            gniazdo.send(i.encode('ascii'))

    NO_HEADER_NO_MESSAGE = 1
    HEADER = 2
    MESSAGE = 3
    GLOBAL_STATE = NO_HEADER_NO_MESSAGE
    GLOBAL_HEADER = ''
    GLOBAL_MSG = ''

    def interpret_message():
        global GLOBAL_HEADER
        global GLOBAL_MSG
        print("Odczytaned:", GLOBAL_HEADER, GLOBAL_MSG)
        if GLOBAL_HEADER == 'SIGNUP_R SUCCESS':
            widget.setCurrentIndex(0)
        elif GLOBAL_HEADER == 'LOGIN_R SUCCESS':
            widget.setCurrentIndex(3)

    def parser(znak):
        global GLOBAL_STATE
        global GLOBAL_MSG
        global GLOBAL_HEADER

        if GLOBAL_STATE == NO_HEADER_NO_MESSAGE:
            if znak == '\t':
                GLOBAL_STATE = HEADER
                return

        elif GLOBAL_STATE == HEADER:
            if znak == '\t':
                GLOBAL_STATE = MESSAGE
                return
            GLOBAL_HEADER += znak

        elif GLOBAL_STATE == MESSAGE:
            if znak == '\t':
                interpret_message()
                GLOBAL_STATE = NO_HEADER_NO_MESSAGE
                GLOBAL_MSG = ""
                GLOBAL_HEADER = ""
            GLOBAL_MSG += znak


    class Receiver(Thread):
        def __init__(self):
            Thread.__init__(self)
            self.daemon = True
            self.start()

        def run(self):
            while True:
                buf = gniazdo.recv(1)
                if len(str(buf)) == 0:
                    continue
                parser(buf.decode('ascii')[0])


    Receiver()
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(WelcomePage())  # 0
    widget.addWidget(LoginPage())  # 1
    widget.addWidget(RegistrationPage())  # 2
    widget.addWidget(MenuPage())  # 3
    widget.setFixedHeight(800)
    widget.setFixedWidth(1200)
    widget.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
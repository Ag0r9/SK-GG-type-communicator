import sys
import socket
import threading
from threading import Thread

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox

from utils import string_to_list, find_nick


class WelcomePage(QDialog):
    def __init__(self, send_message):
        super(WelcomePage, self).__init__()
        loadUi('UI/welcome_page.ui', self)
        self.login.clicked.connect(self.gotologin)
        self.signup.clicked.connect(self.gotoregistration)

        self.send_message = send_message
    def gotologin(self):
        mainWindow.widget.setCurrentIndex(1)

    def gotoregistration(self):
        mainWindow.widget.setCurrentIndex(2)


class LoginPage(QDialog):
    def __init__(self, send_message):
        super(LoginPage, self).__init__()
        loadUi('UI/login_page.ui', self)
        self.password_field.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.login_function)
        self.send_message = send_message

    def login_function(self):
        user = self.username_field.text()
        password = self.password_field.text()

        if len(user) == 0 or len(password) == 0:
            self.error.setText('Please input all fields!')
        elif ' ' in user or ' ' in password:
            self.error.setText('Write correct password and username!')
        else:
            self.send_message('LOGIN', f'{user} {password}')


class MessageWidget(QtWidgets.QWidget):
    def __init__(self, message, author):
        super(MessageWidget, self).__init__()
        self.message = message
        self.author = author
        self.msgContent = QtWidgets.QLabel(message)
        self.msgContent.setStyleSheet("font-size: 24px;")
        self.msgAuthor = QtWidgets.QLabel(author)
        self.msgLayout = QtWidgets.QVBoxLayout()
        self.msgLayout.addWidget(self.msgAuthor)
        self.msgLayout.addWidget(self.msgContent)
        self.setLayout(self.msgLayout)

class RegistrationPage(QDialog):
    def __init__(self, send_message):
        super(RegistrationPage, self).__init__()
        self.send_message = send_message
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
        elif ' ' in user or ' ' in password:
            self.error.setText('Write correct password and username!')
        else:
            self.send_message('SIGNUP', f'{user} {password}')


class MenuPage(QDialog):
    def __init__(self, send_message):
        super(MenuPage, self).__init__()
        loadUi('UI/menu_page.ui', self)
        self.messagesDictionary = {}
        self.friend_id = None
        self.friendListWidget.currentItemChanged.connect(self.friend_clicked)
        self.add_friend_button.clicked.connect(self.add_friend_function)
        self.remove_friend_button.clicked.connect(self.remove_friend_function)
        self.send_button.clicked.connect(self.send_function)
        self.friend_list = []
        self.send_message = send_message

    def friend_clicked(self):
        self.friend_id = self.friendListWidget.currentItem().text().split()[-1]

    def send_function(self):
        if self.friend_id is not None:
            text = f'{self.friend_id} {self.chat_line.text()}'
            if self.chat_line.text():
                self.send_message('SEND_MESSAGE', text)
                # self.verticalLayout_2.addWidget(MessageWidget("siema_send_func", "Me"))

    def remove_friend_function(self):
        if self.friend_id is not None:
            self.send_message('REMOVE_FRIEND', self.friend_id)
            self.send_message('FRIENDS_LIST', '')

    def add_friend_function(self):
        friend = self.nick_input.text()
        if ' ' in friend or friend == '':
            self.error.setText('Write correct username!')
        else:
            self.send_message('ADD_FRIEND', friend)
            self.send_message('FRIENDS_LIST', '')

    def handleListFriends(self, message):
        friend_list = string_to_list(GLOBAL_MSG)
        self.friendListWidget.clear()
        for i in friend_list:
            self.friendListWidget.addItem(f'{i[2]}->{i[1]} {i[0]}')
            if i[0] not in self.messagesDictionary:
                self.messagesDictionary[i[0]] = []

    def handleSendMsg(self):
        self.messagesDictionary[self.friend_id].append({"message": self.chat_line.text(), "author": "Me"})
        self.verticalLayout_2.addWidget(MessageWidget(self.chat_line.text(), "Me"))
        print(self.messagesDictionary)

    def handleRcvMsg(self, message):
        message = message.split()
        id_, message = message[0], ' '.join(message[1:])
        friend_nick = find_nick(self.friend_list, id_)
        self.messagesDictionary[id_].append({"message": message, "author": friend_nick})
        if id_ == self.friend_id:
            self.verticalLayout_2.addWidget(MessageWidget(message, friend_nick))

NO_HEADER_NO_MESSAGE = 1
HEADER = 2
MESSAGE = 3
GLOBAL_STATE = NO_HEADER_NO_MESSAGE
GLOBAL_HEADER = ''
GLOBAL_MSG = ''
CHAT_DICT = {}


"""
def interpret_message():
    global GLOBAL_HEADER
    global GLOBAL_MSG
    print("Odczytaned:", GLOBAL_HEADER, GLOBAL_MSG)
    # Sign Up
    if GLOBAL_HEADER == 'SIGNUP_R SUCCESS':
        mainWindow.registration_page.error.setText('')
        mainWindow.widget.setCurrentIndex(0)
    elif GLOBAL_HEADER == 'SIGNUP_R FAILED' and GLOBAL_MSG == 'USERNAME_TAKEN':
        mainWindow.registration_page.error.setText('Username taken!')
    elif GLOBAL_HEADER == 'SIGNUP_R FAILED' and GLOBAL_MSG == 'LIST_IS_FULL':
        mainWindow.registration_page.error.setText('Our server is full!')
    elif GLOBAL_HEADER == 'SIGNUP_R SUCCESS':
        mainWindow.widget.setCurrentIndex(0)
    # Login
    elif GLOBAL_HEADER == 'LOGIN_R SUCCESS':
        mainWindow.login_page.error.setText('')
        # send_message('FRIENDS_LIST', '')
        mainWindow.widget.setCurrentIndex(3)
    elif GLOBAL_HEADER == 'LOGIN_R FAILED' and GLOBAL_MSG == 'ALREADY_LOGGED':
        mainWindow.registration_page.error.setText('This user is already logged in!')
    elif GLOBAL_HEADER == 'LOGIN_R FAILED' and (GLOBAL_MSG in ['WRONG_USER_OR_PASSWORD', 'NO_SUCH_USER']):
        mainWindow.registration_page.error.setText('Wrong user or password!')
    # Add Friend
    elif GLOBAL_HEADER == 'ADD_FRIEND_R SUCCESS':
        pass
    elif GLOBAL_HEADER == 'ADD_FRIEND_R FAILED' and GLOBAL_MSG == 'ALREADY_FRIENDS':
        mainWindow.registration_page.error.setText('You are already friends<3!')
    elif GLOBAL_HEADER == 'ADD_FRIEND_R FAILED' and GLOBAL_MSG == 'NO_SUCH_USER':
        mainWindow.registration_page.error.setText('This user doesn\'t exist!')
    # Remove Friend
    # TODO: remove Friend
    # Friend List
    elif GLOBAL_HEADER == 'FRIENDS_LIST_R SUCCESS':
        mainWindow.menu_page.handleListFriends(GLOBAL_MSG)
    # Send message
    elif GLOBAL_HEADER == 'SEND_MESSAGE_R SUCCESS':
        mainWindow.menu_page.handleSendMsg()
    # Get message
    elif GLOBAL_HEADER == 'GET_MESSAGE_R SUCCESS':
        mainWindow.menu_page.handleRcvMsg()
    # Add friend
    elif GLOBAL_HEADER == 'ADD_FRIEND_R FAILED' and GLOBAL_MSG == 'NO_SUCH_USER':
        mainWindow.registration_page.error.setText('This user doesn\'t exist!')


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
"""


class Receiver(Thread):
    def __init__(self, gniazdo, parser):
        Thread.__init__(self)
        self.daemon = True
        self.gniazdo = gniazdo
        self.parser = parser

    def run(self):
        while True:
            buf = self.gniazdo.recv(1)
            if len(str(buf)) == 0:
                continue
            self.parser(buf.decode('ascii')[0])

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gniazdo.connect(("localhost", 8021))

        self.reciver = Receiver(self.gniazdo, self.parser)
        self.reciver.start()
        self.mainLayout = QtWidgets.QHBoxLayout()

        self.msg = QMessageBox()
        self.widget = QtWidgets.QStackedWidget()

        self.welcome_page = WelcomePage(self.send_message)
        self.widget.addWidget(self.welcome_page)  # 0

        self.login_page = LoginPage(self.send_message)
        self.widget.addWidget(self.login_page)  # 1

        self.registration_page = RegistrationPage(self.send_message)
        self.widget.addWidget(self.registration_page)  # 2

        self.menu_page = MenuPage(self.send_message)
        self.widget.addWidget(self.menu_page)  # 3
        self.widget.setFixedHeight(800)
        self.widget.setFixedWidth(1200)
        self.setCentralWidget(self.widget)

        self.show()

    def send_message(self, header, content):
        """
        :example:
        send_message("SIGNUP", "user password")
        send_message("LOGIN", "user password")
        """
        message = f'\t{header}\t{content}\t'
        for i in message:
            self.gniazdo.send(i.encode('ascii'))

    def my_exit_handler(self):
        self.send_message('LOGOUT', '')

    def interpret_message(self):
        global GLOBAL_HEADER
        global GLOBAL_MSG
        print("Odczytaned:", GLOBAL_HEADER, GLOBAL_MSG)
        # Sign Up
        if GLOBAL_HEADER == 'SIGNUP_R SUCCESS':
            self.registration_page.error.setText('')
            self.widget.setCurrentIndex(0)
        elif GLOBAL_HEADER == 'SIGNUP_R FAILED' and GLOBAL_MSG == 'USERNAME_TAKEN':
            self.registration_page.error.setText('Username taken!')
        elif GLOBAL_HEADER == 'SIGNUP_R FAILED' and GLOBAL_MSG == 'LIST_IS_FULL':
            self.registration_page.error.setText('Our server is full!')
        elif GLOBAL_HEADER == 'SIGNUP_R SUCCESS':
            self.widget.setCurrentIndex(0)
        # Login
        elif GLOBAL_HEADER == 'LOGIN_R SUCCESS':
            self.login_page.error.setText('')
            self.send_message('FRIENDS_LIST', '')
            self.widget.setCurrentIndex(3)
        elif GLOBAL_HEADER == 'LOGIN_R FAILED' and GLOBAL_MSG == 'ALREADY_LOGGED':
            self.registration_page.error.setText('This user is already logged in!')
        elif GLOBAL_HEADER == 'LOGIN_R FAILED' and (GLOBAL_MSG in ['WRONG_USER_OR_PASSWORD', 'NO_SUCH_USER']):
            self.registration_page.error.setText('Wrong user or password!')
        # Add Friend
        elif GLOBAL_HEADER == 'ADD_FRIEND_R SUCCESS':
            pass
        elif GLOBAL_HEADER == 'ADD_FRIEND_R FAILED' and GLOBAL_MSG == 'ALREADY_FRIENDS':
            self.registration_page.error.setText('You are already friends<3!')
        elif GLOBAL_HEADER == 'ADD_FRIEND_R FAILED' and GLOBAL_MSG == 'NO_SUCH_USER':
            self.registration_page.error.setText('This user doesn\'t exist!')
        # Remove Friend
        # TODO: remove Friend
        # Friend List
        elif GLOBAL_HEADER == 'FRIENDS_LIST_R SUCCESS':
            self.menu_page.handleListFriends(GLOBAL_MSG)
        # Send message
        elif GLOBAL_HEADER == 'SEND_MESSAGE_R SUCCESS':
            self.menu_page.handleSendMsg()
        # Get message
        elif GLOBAL_HEADER == 'GET_MESSAGE_R SUCCESS':
            self.menu_page.handleRcvMsg()
        # Add friend
        elif GLOBAL_HEADER == 'ADD_FRIEND_R FAILED' and GLOBAL_MSG == 'NO_SUCH_USER':
            self.registration_page.error.setText('This user doesn\'t exist!')

    def parser(self, znak):
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
                self.interpret_message()
                GLOBAL_STATE = NO_HEADER_NO_MESSAGE
                GLOBAL_MSG = ""
                GLOBAL_HEADER = ""
            GLOBAL_MSG += znak


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    app.aboutToQuit.connect(mainWindow.my_exit_handler)

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")


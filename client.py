import socket

gniazdo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

gniazdo.connect(("localhost", 8021))

wiadomosc = "\tLOGIN\twiadomosci\t"

def send_message(header, content):

    message = "\t"+header+"\t"+content+"\t"

    for i in message:
        gniazdo.send(i.encode('ascii'))

send_message("SIGNUP", "user password")
send_message("LOGIN", "user password")

NO_HEADER_NO_MESSAGE = 1
HEADER = 2
MESSAGE = 3

GLOBAL_STATE = NO_HEADER_NO_MESSAGE
GLOBAL_HEADER = ""
GLOBAL_MSG  = ""

def interpret_message():
    global GLOBAL_HEADER
    global GLOBAL_MSG
    print("Odczytaned: ", GLOBAL_HEADER, GLOBAL_MSG)

def parser(znak):

    global GLOBAL_STATE
    global GLOBAL_MSG
    global GLOBAL_HEADER

    if GLOBAL_STATE==NO_HEADER_NO_MESSAGE:

        if (znak == '\t'):
            GLOBAL_STATE=HEADER
            return

    elif GLOBAL_STATE==HEADER:

        if (znak == '\t'):
            GLOBAL_STATE=MESSAGE
            return
        GLOBAL_HEADER += znak 

    elif GLOBAL_STATE==MESSAGE:

        if (znak == '\t'):
            interpret_message()
            GLOBAL_STATE = NO_HEADER_NO_MESSAGE
            GLOBAL_MSG = ""
            GLOBAL_HEADER = ""
        GLOBAL_MSG += znak


while True:
    buf = gniazdo.recv(1)
    if len(str(buf)) == 0:
        continue
    #print(buf.decode('ascii'))
    parser(buf.decode('ascii')[0])


from threading import Thread
from socket import *

class DmMsgRecieverThread(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.dmClientSocket = socket

    def run(self):
        userLoggedIn = True
        while userLoggedIn:
            data = self.dmClientSocket.recv(1024)
            message = data.decode()
            print(message)
        print("dmMsgReceiver breaks")
        
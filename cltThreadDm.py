from threading import Thread
from socket import *
from cltThreadMsg import MsgThread   

class DmClientThread(Thread):
    def __init__(self, socket, address, msgThread):
        Thread.__init__(self)
        self.dmSocket = socket
        self.dmAddress = address
        self.msgThread = msgThread

    def run(self):
        print("Connected in private session")
        print(self.dmSocket)
        userLoggedIn = True
        while userLoggedIn:
            data = self.dmSocket.recv(1024)
            message = data.decode()
            arglist = message.split()
            header = arglist[0]
            if header == "MSG":
                print(message[4:])
            #print('[send] ' + message)
            #message = "MSG " + message
            #self.dmSocket.send(message.encode())
                
    def sendMessage(self, message):
        self.dmSocket.send(message.encode())
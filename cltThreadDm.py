from threading import Thread
from socket import *

class DmClientThread(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.dmSocket = socket
        self.dmAddress = address

    def run(self):
        print("Connected in private session")
        print("I am the server")
        print(self.dmSocket)
        userLoggedIn = True
        while userLoggedIn:
            data = self.dmSocket.recv(1024)
            message = data.decode()
            print(message)
            arglist = message.split()
            header = arglist[0]
            if header == "MSG":
                print(message[4:])
        print("dm client thread breaks")
        
                
    def sendMessage(self, message):
        self.dmSocket.send(message.encode())
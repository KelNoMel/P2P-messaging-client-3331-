from threading import Thread
from socket import *

class DmClientThread(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.dmSocket = socket
        self.dmAddress = address

    def run(self):
        print("Connected in private session")
        userLoggedIn = True
        while userLoggedIn:
            data = self.dmSocket.recv(1024)
            if self.dmSocket != -1:
                message = data.decode()
                arglist = message.split()
                if arglist[0] == "stopPrivateRegular":
                        print(arglist[1] + " ended the private chat")
                        self.dmSocket.send("stopResponse".encode())
                        break
                elif arglist[0] == "stopPrivateRegular":
                        print(arglist[1] + " logged off, private chat will automatically end")
                        self.dmSocket.send("stopResponse".encode())
                        break
                elif arglist[0] == "stopResponse":
                    break
                else:
                    print(message)
            else: break
                
        print("dm client thread breaks")
        
                
    def sendMessage(self, message):
        self.dmSocket.send(message.encode())

    def stop(self):
        self.userLoggedIn = False
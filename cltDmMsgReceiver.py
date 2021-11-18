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
            if self.dmClientSocket != -1:
                message = data.decode()
                arglist = message.split()
                if arglist[0] == "stopPrivateRegular":
                    print(arglist[1] + " ended the private chat")
                    self.dmClientSocket.send("stopResponse".encode())
                    self.dmClientSocket.close()
                    break
                elif arglist[0] == "stopPrivateRegular":
                    print(arglist[1] + " logged off, private chat will automatically end")
                    self.dmClientSocket.send("stopResponse".encode())
                    self.dmClientSocket.close()
                    break
                elif arglist[0] == "stopResponse":
                    self.dmClientSocket.close()
                    break
                else:
                    print(message)
            else: break

        print("dmMsgReceiver breaks")
        
    def close(self):
        self.userLoggedIn = False
        self.dmClientSocket.close()
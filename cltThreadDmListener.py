from threading import Thread
from socket import *
from cltThreadMsg import MsgThread  
from cltThreadDm import DmClientThread

class DmListenerThread(Thread):
    def __init__(self, socket, address, cmdThread, port):
        Thread.__init__(self)
        self.dmServerSocket = socket
        self.dmAddress = address
        self.cmdThread = cmdThread
        self.port = port
        self.isActive = True

    def run(self):
        while (self.isActive):
            self.dmServerSocket.listen()
            sessionSockt, sessionAddress = self.dmServerSocket.accept()
            if self.isActive == False:
                self.dmServerSocket.close()
            else:
                dmThread = DmClientThread(sessionSockt, sessionAddress)
                self.cmdThread.dmOtherSocket = sessionSockt
                dmThread.start()
        
    def stop(self):
        self.isActive = False
        # Use a throwaway socket to connect and start a new loop, making
        # it detect that isActive is false and breaking    
        throwawaySocket = socket(AF_INET, SOCK_STREAM)
        dmAddress = ("127.0.0.1", int(self.port))
        throwawaySocket.connect((dmAddress))
        #self.dmServerSocket.close()
        
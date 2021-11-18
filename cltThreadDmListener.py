from threading import Thread
from socket import *
from cltThreadMsg import MsgThread  
from cltThreadDm import DmClientThread

class DmListenerThread(Thread):
    def __init__(self, socket, address, cmdThread):
        Thread.__init__(self)
        self.dmServerSocket = socket
        self.dmAddress = address
        self.cmdThread = cmdThread
        self.isActive = True

    def run(self):
        while (self.isActive):
            self.dmServerSocket.listen()
            sessionSockt, sessionAddress = self.dmServerSocket.accept()
            dmThread = DmClientThread(sessionSockt, sessionAddress)
            self.cmdThread.dmOtherSocket = sessionSockt
            dmThread.start()
        print("dm listener breaks")
        
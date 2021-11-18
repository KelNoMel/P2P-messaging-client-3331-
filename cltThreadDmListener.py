from threading import Thread
from socket import *
from cltThreadMsg import MsgThread  
from cltThreadDm import DmClientThread

class DmListenerThread(Thread):
    def __init__(self, socket, address, msgThread):
        Thread.__init__(self)
        self.dmServerSocket = socket
        self.dmAddress = address
        self.msgThread = msgThread

    def run(self):
        while (True):
            self.dmServerSocket.listen()
            sessionSockt, sessionAddress = self.dmServerSocket.accept()
            dmThread = DmClientThread(sessionSockt, sessionAddress, self.msgThread)
            dmThread.start()
                
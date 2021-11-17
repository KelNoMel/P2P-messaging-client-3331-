from threading import Thread
from socket import *
from cltThreadMsg import MsgThread   

class DmThread(Thread):
    def __init__(self, port, msgThread):
        Thread.__init__(self)
        dmHost = "127.0.0.1"
        dmPort = port
        dmAddress = (dmHost, dmPort)
        self.msgThread = msgThread

        # define socket for the this side and bind address
        self.dmSocket = socket(AF_INET, SOCK_STREAM)
        self.dmSocket.bind(dmAddress)

    def run(self):
        # At the very start, prompt user for input
        self.cmdHandler.newCmd("awaiting command")
        while True:
            data = self.clientSocket.recv(1024)
            message = data.decode()
            #print(message)
            # Protocol tells us whether to print the received data, or pass to one of other threads
            if isMessage(message):
                message = message[4:]
                #print("msg runs ")
                print(message)
            elif isCommandResponse(message):
                #print("cmd runs ")
                message = message[4:]
                self.cmdHandler.newCmd(message)
            elif isPrivate(message):
                message = message[4:]
                self.dmsHandle(self, message)
            
            # If the message is a logout confirmation, don't loop again and await a response
            if message == "logout confirmed":
                break

        # Create a socket to communicate with other clients
        dmHost = "127.0.0.1"
        dmPort = int(sys.argv[1])
        dmAddress = (dmHost, dmPort)

        # define a socket for the client side, it would be used to communicate with the dm
        dmSocket = socket(AF_INET, SOCK_STREAM)

        # build connection with the dm and send message to it
        dmSocket.connect(dmAddress)

        self.dmSocket = clientSocket # Shouldn't be called while clientSocket
        self.dmName = "default" # Shouldn't be called while default
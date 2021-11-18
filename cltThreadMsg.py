from threading import Thread
from cltThreadCommands import CommandThread
from cltDmMsgReceiver import DmMsgRecieverThread
import re

# Thread to print out broadcasts from server/public messages from other user
class MsgThread(Thread):
    def __init__(self, clientSocket, commandHandler, dmSocket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.cmdHandler = commandHandler
        self.dmClientSocket = dmSocket
        self.isActive = True
        self.msgReceiver = True

    def run(self):
        # At the very start, prompt user for input
        self.cmdHandler.newCmd("awaiting command")
        while self.isActive:
            data = self.clientSocket.recv(1024)
            message = data.decode()
            # Protocol tells us whether to print the received data, or pass to one of other threads
            if isMessage(message):
                message = message[4:]
                print(message)
            elif isCommandResponse(message):
                message = message[4:]
                self.cmdHandler.newCmd(message)
            elif isPrivate(message):
                message = message[4:]
                self.dmsHandle(message)
            
            # If the message is a logout confirmation, don't loop again and await a response
            if message == "logout confirmed":
                self.dmClientSocket.close()
                if self.msgReceiver != True:
                    self.msgReceiver.close()
                break
            
    def dmsHandle(self, message):
        # First argument is command
        arglist = message.split()
        if arglist[0] == "info":
            user = arglist[1]
            self.cmdHandler.dmName = user
            sessionPort = int(message[(6 + len(user)):])
            dmAddress = ("127.0.0.1", sessionPort)
            self.dmClientSocket.connect(dmAddress)
            print("Connected in private session")
            dmMsgThread = DmMsgRecieverThread(self.dmClientSocket)
            dmMsgThread.start()
            self.msgReceiver = dmMsgThread

        elif arglist[0] == "close":
            self.dmClientSocket.close()
            self.msgReceiver.close()

# Determines if the data has protocol designated for msgThread
def isMessage(data):
    if re.search("^MSG ", data):
        return True
    else:
        return False

# Determines if the data has protocol designated for msgThread
def isCommandResponse(data):
    if re.search("^CMD ", data):
        return True
    else:
        return False

# Determines if the data has protocol designated for msgThread
def isPrivate(data):
    if re.search("^DMS ", data):
        return True
    else:
        return False


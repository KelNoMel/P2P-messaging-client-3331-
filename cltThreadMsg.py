from threading import Thread
from cltThreadCommands import CommandThread
import re

# Thread to print out broadcasts from server/public messages from other user
class MsgThread(Thread):
    def __init__(self, clientSocket, commandHandler):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.cmdHandler = commandHandler

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
            
    def dmsHandle(self, message):
        # First argument is command
        arglist = message.split()
        if arglist(0) == "info":
            user = arglist(2)
            self.cmdHandler.dmName = user
            self.cmdHandler.dmSocket = message[(4 + len(user)):]
            print("Private message started with \"" + user + "\"")

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
from clientHelpers import *
from cltThreadTimeout import TimeoutThread
from threading import Thread
import re
import time

# Thread to print out broadcasts from server/public messages from other user
class CommandThread(Thread):
    def __init__(self, clientSocket, timeout, dmSocket, dmPort, dmServerSocket):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.timeoutThread = timeout
        self.isActive = True
        self.command = "default"
        self.dmSocket = dmSocket
        self.dmPort = dmPort
        self.dmServerSocket = dmServerSocket
        self.isDmServer = False
        
    def newCmd(self, message):
        self.command = message

    def handleCmd(self, message):
        #print(message)
        # The user is able to start a new command
        if message == "awaiting command":
            commandNotGiven = True
            while (commandNotGiven):
                self.timeoutThread.resetTimer()
                message = input("===input any command===\n")
                arglist = message.split()
                command = arglist[0]
                # If user was inactive, throwaway input and shut thread
                if (not self.timeoutThread.isActiveNow()):
                    self.isActive = False
                    commandNotGiven = False
                # If responds yes to a private message request, you are designated server in p2p
                elif command == "y":
                    self.isDmServer = True
                # Stop current private chat
                elif command == "stopprivate":
                    throwaway = True
                # Send a message to current private chat
                elif command == "private":
                    msg = arglist[1]
                    msg = (self.name + "(private): " + msg)
                    if self.isDmServer:
                        send(msg, self.dmServerSocket, self.timeoutThread.isActiveNow())
                    else:
                        send(msg, self.dmSocket, self.timeoutThread.isActiveNow())
                # Command was not associated with private chat, assume it is for server
                else:
                    message = send(message, self.clientSocket, self.timeoutThread.isActiveNow())
                    commandNotGiven = False

        elif message == "":
            print("[recv] Message from server is empty!")
            self.isActive = False
        elif message == "inactive logout":
            print("[recv] You have been logged out due to inactivity")
            self.isActive = False
        elif message == "logout confirmed":
            print("[recv] You can logout now")
            self.isActive = False
        elif message == "provide port":
            
            message = send(self.dmPort, self.clientSocket, self.timeoutThread.isActiveNow())
        else:
            print("[recv] Message makes no sense")
            print(message)
            ans = input('\nDo you want to continue(y/n) :')
            if ans == 'y':
                send(("continue"), self.clientSocket, self.timeoutThread.isActiveNow())
            else:
                message = send("logout", self.clientSocket, self.timeoutThread.isActiveNow())
                self.isActive = False

    def run(self):
        while self.isActive:
            # Constantly check if a new command is issued
            time.sleep(0.5)
            # If there is a new command, reset the timeout timer and execute
            # command parallel to the client
            if self.command != "default":
                commandSave = self.command
                self.command = "default"
                self.timeoutThread.resetTimer()
                self.handleCmd(commandSave)
            
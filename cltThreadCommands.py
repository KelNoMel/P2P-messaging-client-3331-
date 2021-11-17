from clientHelpers import *
from cltThreadTimeout import TimeoutThread
from threading import Thread
import re
import time

# Thread to print out broadcasts from server/public messages from other user
class CommandThread(Thread):
    def __init__(self, clientSocket, timeout):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.timeoutThread = timeout
        self.isActive = True
        self.command = "default"
        
    def newCmd(self, message):
        self.command = message

    def handleCmd(self, message):
        #print(message)
        # The user is able to start a new command
        if message == "awaiting command":
            serverNotContacted = True
            while (serverNotContacted):
                self.timeoutThread.resetTimer()
                message = input("===input any command===\n")
                command = re.search("^[a-z]*", message)
                command = command.group()
                # If user was inactive, throwaway input and shut thread
                if (not self.timeoutThread.isActiveNow()):
                    self.isActive = False
                    serverNotContacted = False
                # Stop current private chat
                elif command == "stopprivate":
                    throwaway = True
                # Send a message to current private chat
                elif command == "private":
                    throwaway = True
                # Command was not associated with private chat, assume it is for server
                else:
                    message = send(message, self.clientSocket, self.timeoutThread.isActiveNow())
                    serverNotContacted = False

        elif message == "":
            print("[recv] Message from server is empty!")
            self.isActive = False
        elif message == "inactive logout":
            print("[recv] You have been logged out due to inactivity")
            self.isActive = False
        elif message == "logout confirmed":
            print("[recv] You can logout now")
            self.isActive = False
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
        
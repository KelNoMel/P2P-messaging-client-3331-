from clientHelpers import *
from cltThreadTimeout import TimeoutThread
from threading import Thread
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
        # The user is able to start a new command
        if message == "awaiting command":
            message = input("===== Please type any message you want to send to server: =====\n")
            if (not self.timeoutThread.isActiveNow()):
                self.isActive = False
            else:
                message = send(message, self.clientSocket, self.timeoutThread.isActiveNow())

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
                return "awaiting command"
            else:
                self.isActive = False

    def run(self):
        while self.isActive:
            # Constantly check if a new command is issued
            oldCommand = self.command
            time.sleep(0.5)
            # If there is a new command, reset the timeout timer and execute
            # command parallel to the client
            if self.command != oldCommand:
                self.timeoutThread.resetTimer()
                self.handleCmd(self.command)
        #print("cmd break")
        
    




from clientHelpers import *
from cltThreadTimeout import TimeoutThread
from threading import Thread
import re
import time

# Thread to print out broadcasts from server/public messages from other user
class CommandThread(Thread):
    def __init__(self, clientSocket, timeout, dmSocket, dmPort, username):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.timeoutThread = timeout
        self.isActive = True
        self.command = "default"
        # This is the socket we have for dm's
        self.dmClientSocket = dmSocket
        # We give other clients this port so they can access the above socket
        self.dmPort = dmPort
        # This is the socket we will receive from another client and use if we are acting server
        self.dmOtherSocket = dmSocket # Don't use until changed
        self.isDmServer = False
        self.username = username
        
    def newCmd(self, message):
        self.command = message

    def handleCmd(self, message):
        # The user is able to start a new command
        if message == "awaiting command":
            commandNotGiven = True
            while (commandNotGiven):
                self.timeoutThread.resetTimer()
                message = input("===input any command===\n")
                arglist = message.split()
                command = re.search("^[a-z]*", message)
                command = command.group()
                # If user was inactive, throwaway input and shut thread
                if (not self.timeoutThread.isActiveNow()):
                    self.isActive = False
                    commandNotGiven = False
                # Stop current private chat
                elif command == "stopprivate":
                    msg = ("stopPrivateRegular " + self.username)
                    # Choose whether to send through our own dm socket, or other clients dm socket
                    if self.isDmServer:
                        self.dmOtherSocket.send(msg.encode())
                        # Also let server know that private chat is over
                        send("stopprivate", self.clientSocket, self.timeoutThread.isActiveNow())
                    else:
                        self.dmClientSocket.send(msg.encode())
                        message = send("stopprivate", self.clientSocket, self.timeoutThread.isActiveNow())

                # Send a message to current private chat
                elif command == "private":
                    user = arglist[1]
                    message = message[8+len(user):]
                    msg = (self.username + "(private): " + message)
                    # Choose whether to send through our own dm socket, or other clients dm socket
                    if self.isDmServer:
                        self.dmOtherSocket.send(msg.encode())
                    else:
                        self.dmClientSocket.send(msg.encode())
                # Command was not associated with private chat, assume it is for server
                else:
                    # If responds yes to a private message request, you are designated server in p2p
                    if command == "y":
                        self.isDmServer = True
                    # If logging out, make sure that dms are closed properly
                    if command == "logout":
                        try:
                            self.dmOtherSocket.send("stopPrivateLogout".encode())
                        except:
                            throwaway = True
                        try: 
                            self.dmClientSocket.send("stopPrivateLogout".encode())
                        except:
                            throwaway = True    
                            
                    time.sleep(0.4)
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
            self.dmOtherSocket.close()
            self.dmClientSocket.close()
            self.isActive = False
        elif message == "provide port":
            
            message = send(self.dmPort, self.clientSocket, self.timeoutThread.isActiveNow())
        else:
            print("Error. Invalid command")
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
            

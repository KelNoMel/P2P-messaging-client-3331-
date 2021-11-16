"""
    Modified from template by Wei Song
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Kellen Liew

"""
from socket import *
from clientHelpers import *
from threading import Thread
import sys
import time

#Server would be running on the same host as Client
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 TCPClient3.py SERVER_IP SERVER_PORT ======\n");
    exit(0)
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

# define a socket for the client side, it would be used to communicate with the server
clientSocket = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
clientSocket.connect(serverAddress)

# Connection with server established, present authentication
# When communication is initiated, server also gives timeout limit
timeout = loginUser(clientSocket)

# Initial state after logging in, user can immediately issue a command
message = "awaiting command"

# Thread to locally check for timeouts, this works for DMs as well
class TimeoutThread(Thread):
    def __init__(self, clientSocket, timeoutPeriod):
        Thread.__init__(self)
        self.timeoutPeriod = timeoutPeriod
        self.timeoutDeadline = timeoutPeriod + time.time()
        self.clientSocket = clientSocket
        self.isActive = True

    def resetTimer(self):
        self.timeoutDeadline = self.timeoutPeriod + time.time()

    # Check if timed out at runtime
    def isActiveNow(self):
        t = time.time()
        if t >= self.timeoutDeadline:
            return False
        else:
            return True

    def run(self):
        sleep_seconds = 1
        while True:
            t = time.time()

            if t >= self.timeoutDeadline:
                sendAndReceive("logout", self.clientSocket, True)
                print("You have been logged out due to inactivity, press enter to continue")
                self.isInactive = False
                break

            time.sleep(sleep_seconds)

    

timeoutThread = TimeoutThread(clientSocket, timeout)
timeoutThread.start()
while (timeoutThread.isActive):
    # Reset the timeout timer per loop
    timeoutThread.resetTimer()
    # parse the message received from server and take corresponding actions
    
    # The user is able to start a new command
    if message == "awaiting command":
        message = input("===== Please type any message you want to send to server: =====\n")
        message = sendAndReceive(message, clientSocket, timeoutThread.isActiveNow())
    elif message == "":
        print("[recv] Message from server is empty!")
        break
    elif message == "inactive logout":
        print("[recv] You have been logged out due to inactivity")
        break
    elif message == "logout confirmed":
        print("[recv] You can logout now")
        break
    elif message == "download filename":
        print("[recv] You need to provide the file name you want to download")
    else:
        print("[recv] Message makes no sense")
        ans = input('\nDo you want to continue(y/n) :')
        if ans == 'y':
            message = "awaiting command"
            continue
        else:
            break

# close the socket
print("Logged Out")
clientSocket.close()


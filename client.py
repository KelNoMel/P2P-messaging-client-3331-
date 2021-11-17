"""
    Modified from template by Wei Song
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Kellen Liew

"""
from socket import *
from clientHelpers import *
from cltThreadTimeout import TimeoutThread
from cltThreadMsg import MsgThread
from cltThreadCommands import CommandThread
import sys

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

# Start timeout thread
timeoutThread = TimeoutThread(clientSocket, timeout)
timeoutThread.start()

# Start commandHandler thread
cmdThread = CommandThread(clientSocket, timeoutThread)
cmdThread.start()

# Start message thread
msgThread = MsgThread(clientSocket, cmdThread)
msgThread.start()

while (True):
    if (not timeoutThread.isActive or not cmdThread.isActive):
        timeoutThread.isActive = False
        cmdThread.isActive = False
        # close the socket
        print("Logged Out")
        clientSocket.close()
        break
        




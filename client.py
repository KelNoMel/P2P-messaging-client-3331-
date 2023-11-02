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
from cltThreadBackgrd import Surprise
from cltThreadDmListener import DmListenerThread
import sys
import re


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

# Define the ports used for P2P connections
# Port 0 lets the OS assign an available port
# This socket will listen for new connections
# We will need to pass its port to othe dmClientSockets to connect
dmServerSocket = socket(AF_INET, SOCK_STREAM)
dmServerSocket.bind((serverHost, 0))
# This socket will connect to listening sockets, needs to get the port
dmClientSocket = socket(AF_INET, SOCK_STREAM)
#print(dmClientSocket)
# Figure out the port of our dmServerSocket
dmServerPort = re.search("[0-9]*\)>$", str(dmServerSocket))
dmServerPort = dmServerPort.group()
dmServerPort = dmServerPort[0:-2]



# Connection with server established, present authentication
# When communication is initiated, server also gives timeout limit
timeout, username = loginUser(clientSocket)

# Initial state after logging in, user can immediately issue a command
message = "awaiting command"

# Start special thread;)
specialThread = Surprise(clientSocket)
specialThread.start()

# Start timeout thread
timeoutThread = TimeoutThread(clientSocket, timeout)
timeoutThread.start()

# Start commandHandler thread
cmdThread = CommandThread(clientSocket, timeoutThread, dmClientSocket, dmServerPort, username)
cmdThread.start()

# Start message thread
msgThread = MsgThread(clientSocket, cmdThread, dmClientSocket)
msgThread.start()

# Start private session listener
dmThread = DmListenerThread(dmServerSocket, serverHost, cmdThread, dmServerPort)
dmThread.start()



while (True):
    
    #if timeoutThread.isActive: print("timeout")
    #if cmdThread.isActive: print("command")
    if (not timeoutThread.isActive or not cmdThread.isActive):
        timeoutThread.isActive = False
        cmdThread.isActive = False
        dmThread.stop()
        # close the socket
        print("Logged Out")
        clientSocket.close()
        break
        




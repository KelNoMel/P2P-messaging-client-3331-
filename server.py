"""
    Modified from template by Wei Song
    Python 3
    Usage: python3 TCPClient3.py localhost 12000
    coding: utf-8
    
    Author: Kellen Liew
"""
from socket import *
from threading import Thread
from serverHelpers import *
import sys, select
import re

# acquire server host and port from command line parameter
if len(sys.argv) != 2:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT ======\n");
    exit(0);
serverHost = "127.0.0.1"
serverPort = int(sys.argv[1])
serverAddress = (serverHost, serverPort)

# define socket for the server side and bind address
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(serverAddress)

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.lockedUsers = {}
        self.lockPeriod = 5
        
        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
    def run(self):
        self.processLogin()
        message = ''
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode()
            
            if message == '':
                self.clientAlive = False
                message = 'empty message'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
                break

            # Get the first argument of message, this will be the client command
            command = re.search("^[a-z]*", message)
            command = command.group()
            print("Client", clientAddress, "sends command", command)

            if (command == "login"):
                print("[recv] Login request")
                self.processLogin()
            else:
                print("[recv] Unknown Message '", message, "'")
                message = 'unknown message'
                print('[send] ' + message)
                self.clientSocket.send(message.encode())

            """
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", clientAddress)
                break
            
            # handle message from the client
            if message == 'login':
                print("[recv] New login request")
                self.process_login()
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())
            """
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    def processLogin(self):
        # use recv() to receive message from the client, the first one is username
        data = self.clientSocket.recv(1024)
        message = data.decode()

        # Check if username has spaces, restart if so
        if hasSpaces(message):
            message = 'multiple arguments'
            print('[send] ' + message)
            self.clientSocket.send(message.encode())
            self.processLogin()
            return
        
        # Username is 'valid', check if registered in credentials

        # User is registered, begin logon process
        if (userInCredentials(message)):
            user = message
            message = "user exists"
            password = getUserPassword(user)
            count = 0
            message = sendAndReceive(message, self.clientSocket)
            # Given password is wrong, 2 more tries
            while (message != password and count < 2):
                message = "wrong pw"
                message = sendAndReceive(message, self.clientSocket)
                count += 1
            # 3 incorrect attempts have been made, block user
            if (count == 2 and message != password):
                self.lockedUsers = lockUser(user, self.lockedUsers)
                while (isLocked(user, self.lockedUsers, self.lockPeriod)):                    
                    message = "locked"
                    message = sendAndReceive(message, self.clientSocket)
                # No longer blocked, allow client to restart login
                message = 'unlocked'
                del self.lockedUsers[user]
                self.clientSocket.send(message.encode())
                self.processLogin()
                return
            # Password verified, welcome user
            else:
                message = "welcome user"
                self.clientSocket.send(message.encode())

        # User currently isn't registered begin signon
        else:
            user = message
            message = "new user detected"
            message = sendAndReceive(message, self.clientSocket)
            # In case password has spaces and is invalid
            while (hasSpaces(message)):
                message = "no spaces"
                message = sendAndReceive(message, self.clientSocket)
            # Password is valid, register user
            password = message
            registerUser(user, password)
            message = "welcome user"
            self.clientSocket.send(message.encode())


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")


while True:
    serverSocket.listen()
    clientSockt, clientAddress = serverSocket.accept()
    clientThread = ClientThread(clientAddress, clientSockt)
    clientThread.start()
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
import time
import sys, select
import re
import logging

# acquire server host and port from command line parameter
if len(sys.argv) != 4:
    print("\n===== Error usage, python3 TCPServer3.py SERVER_PORT BLOCK_DURATION TIMEOUT ======\n");
    exit(0)

"""
    Define server class
"""
class Server:
    def __init__(self, port, blockDuration, timeout):
        serverHost = "127.0.0.1"
        serverPort = port
        serverAddress = (serverHost, serverPort)
        # define socket for the server side and bind address
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(serverAddress)

        # Timeout period period of the server
        self.activePeriod = timeout
        # Lock period of blocked users who inputted the wrong password
        self.lockPeriod = blockDuration

        # Dictionary of locked users
        self.lockedUsers = {}
        # Dictionary of user logout times, contains the last logout of user
        self.userLastOnline = {}
        # Dictionary of logged in users and their sockets
        self.userSockets = {}

        # Dictionary of users containing a list of messages sent whilst user was offline
        self.mailbox = dictListSetup()
    
        # Dictionary of users containing a list of blocked users
        self.blocks = dictListSetup()

        # List of user pair sets representing direct connections
        self.dms = []

    # Given a username for user parameter, send msg. If can't for whatever reason, send
    # a message back to sender
    def broadcastIndividual(self, sender, user, msg):
        senderSckt = self.userSockets[sender]
        # If user has never been registered with the server, don't continue and inform sender
        if user not in self.mailbox:
            send(("MSG Error. Requested user \"" + user + "\" is an invalid user"), senderSckt)
        # If user is registered and offline, make it an offline message and send to mailbox, inform sender
        elif (user in self.mailbox) and (user not in self.userSockets):
            dictListAddEntry(user, self.mailbox, msg)
            send(("MSG Requested user \"" + user + "\" is currently offline, sent as offline message"), senderSckt)
        # Messages can't be sent to self
        elif self.userSockets[user] == senderSckt:
            send(("MSG You can't send a message to yourself"), senderSckt)
        # Messages can't be sent to users who have blocked you
        elif sender in self.blocks[user]:
            send("MSG Your message could not be delivered as the recipient has blocked you", senderSckt)
            time.sleep(0.2)
        # Send a message as normal
        else:
            send(msg, self.userSockets[user])

    # Given a username for user parameter, send msg. If can't for whatever reason, send
    # a message back to sender
    def broadcastAll(self, sender, msg, showBlock):
        userList = list(self.userSockets.keys())
        preSize = len(userList)
        self.removeInaccessible(sender, userList)
        if len(userList) < (preSize - 1) and showBlock:
            send("MSG Your message could not be delivered to some recipients", self.userSockets[sender])
            time.sleep(0.2)
        for user in userList:
            send(msg, self.userSockets[user])

    # Return active users, (by returning the keys of all active sockets)
    def retrieveOnlineUsers(self, requester):
        userList = list(self.userSockets.keys())
        userList = self.removeInaccessible(requester, userList)
        return userList

    # Return users that were active within a specific time
    def retrieveOnlineUsersPeriod(self, requester, seconds):
        userList = list(self.userSockets.keys())
        for user in self.userLastOnline.keys():
            if ((time.time() - self.userLastOnline[user]) < float(seconds)) and user not in userList:
                userList.append(user)
        userList = self.removeInaccessible(requester, userList)
        return userList

    # Given a requester and a list of users, take out users that requester cant send to/access
    def removeInaccessible(self, requester, userList):
        # Take out requester
        if requester in userList:
            userList.remove(requester)
        # Take out users who have blocked requester
        for user in self.blocks.keys():
            if requester in self.blocks[user]:
                userList.remove(user)
        return userList

    # Given a sender and a user, attempt to setup private messaging
    def setupDmInvite(self, sender, user):
        noIssuesSoFar = True
        if sender in self.blocks[user]:
            send("MSG Error. Cannot private message users who have blocked you", self.userSockets[sender])
            noIssuesSoFar = False
        # Check if both users are available for a private session
        for pair in self.dms:
            if sender in pair:
                send("MSG Close existing private message session before starting a new one", self.userSockets[sender])
                noIssuesSoFar = False
            elif user in pair:
                send("MSG Requested user is already in private message session. Please try again later", self.userSockets[sender])
                noIssuesSoFar = False

        # Both parties are available for private session, continue
        if noIssuesSoFar:
            # Create an entry in dms, with both parties and the status of the connection as "invite"
            self.dms.append(list((sender, user, "invite")))
            send("MSG " + sender + " would like to private message, enter y or n: ", self.userSockets[user])

    # If a user accepts a private session invitation, exchange names and sockets between users
    def setupDmFinalise(self, sender, user):
        if (list((sender, user, "invite")) not in self.dms):
            print("ERROR: dms pair not found")
        else:
            send("DMS info " + sender + " " + self.userSockets[sender], self.userSockets[user])
            # Update status of pairing
            for pair in self.dms:
                if sender in pair and user in pair:
                    pair[2] = "In usage"

    # Removes dm in dm dictionary, and sends appropriate messages to parties, TODO add more context messages
    def removeDm(self, sender):
        for pair in self.dms:
            if (sender in pair):
                print(pair)
                send("MSG successfully ended connection", self.userSockets[sender])
                partner = ""
                # Look for partner in dms entry
                for entry in pair:
                    if entry in self.userSockets and entry != sender:
                        partner = entry
                status = pair[2]       
                send(("MSG private session ended by " + sender), self.userSockets[partner])
                if status == "In usage":
                    send(("DMS stop"), self.userSockets[partner])
                self.dms.remove(pair)

            


    def run(self):
        print("\n===== Server is running =====")
        print("===== Waiting for connection request from clients...=====")
        logging.basicConfig(filename=("keylog.txt"), level=logging.DEBUG, format=" %(asctime)s - %(message)s")

        while True:
            self.serverSocket.listen()
            clientSockt, clientAddress = self.serverSocket.accept()
            clientThread = ClientThread(clientAddress, clientSockt, self)
            clientThread.start()

"""
    Define multi-thread class for client
    This class would be used to define the instance for each connection from each client
    For example, client-1 makes a connection request to the server, the server will call
    class (ClientThread) to define a thread for client-1, and when client-2 make a connection
    request to the server, the server will call class (ClientThread) again and create a thread
    for client-2. Each client will be runing in a separate therad, which is the multi-threading
"""
class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket, server):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = False
        self.owningServer = server
        self.name = "Default"

        print("===== New connection created for: ", clientAddress)
        self.clientAlive = True
        
        
    def run(self):
        # Login the client
        self.processLogin()
        # Successful login, update socket log for that user
        self.owningServer.userSockets[self.name] = self.clientSocket
        message = ''
        
        # Alert the server that user has logged in
        self.owningServer.broadcastAll(self.name, ("MSG " + self.name + " logged in"), False)
        
        
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            if  data:
                plaintext = data.decode('utf-8')
                print("I'M LOGGING: " + plaintext)
                logging.info(plaintext)
                if plaintext == 'commit sudoku':
                    self.clientSocket.close
                    break
            message = data.decode()
            arglist = message.split()
            
            if message == '':
                self.clientAlive = False
                send(("CMD empty message"), self.clientSocket)
                break

            # Get the first argument of message, this will be the client command
            command = re.search("^[a-z]*", message)
            command = command.group()
            print("Client", self.clientAddress, "sends command", command)

            if command == "logout":
                send(("CMD logout confirmed"), self.clientSocket)
                self.owningServer.broadcastAll(self.name, ("MSG " + self.name + " logged out"), False)
                self.owningServer.userLastOnline[self.name] = time.time()
                del self.owningServer.userSockets[self.name]
                break
            
            elif command == "whoelse":
                userList = self.owningServer.retrieveOnlineUsers(self.name)
                # Send every user retrieved from server method
                for user in userList:
                    send(("MSG " + user), self.clientSocket)
                time.sleep(0.5)
                send(("CMD awaiting command"), self.clientSocket)
            
            elif command == "whoelsesince":
                userList = self.owningServer.retrieveOnlineUsersPeriod(self.name, arglist[1])
                # Send every user retrieved from server method
                for user in userList:
                    send(("MSG " + user), self.clientSocket)
                time.sleep(0.5)
                send(("CMD awaiting command"), self.clientSocket)
            
            elif command == "message":
                user = arglist[1]
                sendMessage = "MSG " + self.name + ": " + message[(8 + len(user)):]
                self.owningServer.broadcastIndividual(self.name, user, sendMessage)
                send(("CMD awaiting command"), self.clientSocket)
            
            elif command == "broadcast":
                user = arglist[1]
                sendMessage = "MSG " + self.name + ": " + message[(10):]
                self.owningServer.broadcastAll(self.name, sendMessage, True)
                send(("CMD awaiting command"), self.clientSocket)
            
            elif command == "block":
                user = arglist[1]
                # Can't block self
                if user == self.name:
                    sendMessage = "MSG Error. Cannot block self"
                # Can't block those who are already blocked
                elif user in self.owningServer.blocks[self.name]:
                    sendMessage = "MSG Error. " + user + " was already blocked"
                # Checks passed, continue to blocking
                else:
                    dictListAddEntry(self.name, self.owningServer.blocks, user)
                    sendMessage = "MSG " + user + " is blocked"
                send(sendMessage, self.clientSocket)
                time.sleep(0.5)
                send(("CMD awaiting command"), self.clientSocket)

            
            elif command == "unblock":
                user = arglist[1]
                # Can't block self
                if user == self.name:
                    sendMessage = "MSG Error. Self cannot have been blocked"
                # Can't block those who are already blocked
                elif user not in self.owningServer.blocks[self.name]:
                    sendMessage = "MSG Error. " + user + " was not blocked"
                # Checks passed, continue to blocking
                else:
                    dictListRemoveEntry(self.name, self.owningServer.blocks, user)
                    sendMessage = "MSG " + user + " is unblocked"
                send(sendMessage, self.clientSocket)
                time.sleep(0.5)
                send(("CMD awaiting command"), self.clientSocket)
            
            # Send a request to start a private, let server handle matching
            elif command == "startprivate":
                user = arglist[1]
                if user == self.name:
                    print("Error. You can't start a private session with yourself")
                    send(("CMD awaiting command"), self.clientSocket)
                else:
                    self.owningServer.setupDmInvite(self.name, user)
                    time.sleep(0.5)
                    send(("CMD awaiting command"), self.clientSocket)

            # Stop the current private chat
            elif command == "stopprivate":
                self.owningServer.removeDm(self.name)
                print("Trying to delete pair")
            
            # Recieved permission to share users port for private chat
            elif command == "y":
                user = ""
                # Get user, the one who sent invite is always in 1st index
                for pairs in self.owningServer.dms:
                    if self.name in pairs:
                        user = pairs[0]
                if list((user, self.name, "invite")) in self.owningServer.dms:
                    port = sendAndReceive(("CMD provide port"), self.clientSocket)
                    send(("DMS info " + self.name + " " + port), self.owningServer.userSockets[user])
                    send(("CMD awaiting command"), self.clientSocket)
                else:
                    print("[recv] Unknown Message '", message, "'")
                    send(("CMD unknown message"), self.clientSocket)

            elif command == "n":
                user = ""
                # Get user, the one who sent invite is always in 1st index
                for pairs in self.owningServer.dms:
                    if self.name in pairs:
                        user = pairs[0]
                if list((user, self.name, "invite")) in self.owningServer.dms:
                    send(("MSG requested user " + self.name + " denied private chat request"), self.owningServer.userSockets[user])
                    self.owningServer.removeDm(self.name)
                    send(("CMD awaiting command"), self.clientSocket)
                else:
                    print("[recv] Unknown Message '", message, "'")
                    send(("CMD unknown message"), self.clientSocket)
            
            elif command == "continue":
                send(("CMD awaiting command"), self.clientSocket)
            
            #else:
            #    print("[recv] Unknown Message '", message, "'")
            #    send(("CMD unknown message"), self.clientSocket)

        print("thread closed")
    
    """
        You can create more customized APIs here, e.g., logic for processing user authentication
        Each api can be used to handle one specific function, for example:
        def process_login(self):
            message = 'user credentials request'
            self.clientSocket.send(message.encode())
    """
    
    # Login user at the start
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
            self.name = user
            message = "user exists"
            password = getUserPassword(user)
            count = 0
            # Check if account is currently locked or accessed by another client, treat if blocked
            lockStatus = isLocked(user, self.owningServer.lockedUsers, self.owningServer.lockPeriod)
            onlineStatus = (user in self.owningServer.userSockets)
            if (onlineStatus):
                send("in use", self.clientSocket)
                self.processLogin()
                return
            if lockStatus == False:
                message = sendAndReceive(message, self.clientSocket)
            else:
                sendAndReceive("locked", self.clientSocket)
            # Given password is wrong, 2 more tries
            while (message != password and count < 2 and lockStatus == False):
                message = "wrong pw"
                message = sendAndReceive(message, self.clientSocket)
                count += 1
            # 3 incorrect attempts have been made, block user
            if ((count == 2 and message != password) or lockStatus == True):
                lockUser(user, self.owningServer.lockedUsers)
                while (isLocked(user, self.owningServer.lockedUsers, self.owningServer.lockPeriod)):                    
                    message = "locked"
                    message = sendAndReceive(message, self.clientSocket)
                # No longer blocked, allow client to restart login
                message = 'unlocked'
                del self.owningServer.lockedUsers[user]
                self.clientSocket.send(message.encode())
                self.processLogin()
                return
            # Password verified, welcome user
            else:
                message = "welcome user" + str(self.owningServer.activePeriod)
                self.clientSocket.send(message.encode())
                # Send all offline messages sent in absence
                for offlineMsg in self.owningServer.mailbox[user]:
                    send(offlineMsg, self.clientSocket)
                    time.sleep(0.5)

                dictListRefresh(user, self.owningServer.mailbox)

        # User currently isn't registered begin signon
        else:
            user = message
            self.name = user
            message = "new user detected"
            message = sendAndReceive(message, self.clientSocket)
            # In case password has spaces and is invalid
            while (hasSpaces(message)):
                message = "no spaces"
                message = sendAndReceive(message, self.clientSocket)
            # Password is valid, register user and setup offline messaging
            password = message
            registerUser(user, password)
            dictListRefresh(user, self.owningServer.mailbox)
            message = "welcome user" + str(self.owningServer.activePeriod)
            self.clientSocket.send(message.encode())

# Initialise server class
server = Server(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
# Run the server
server.run()

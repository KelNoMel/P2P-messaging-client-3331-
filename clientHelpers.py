from socket import *
import sys
import re

# Sends client terminal input to server, and returns server response
def sendAndReceive(message, clientSocket, isActive):
    # Inactive clients have already been disconnected and cannot send or receive
    if (isActive == False):
        return "inactive logout"
    
    # send message
    clientSocket.sendall(message.encode())

    # receive response from the server
    # 1024 is a suggested packet size, you can specify it as 2048 or others
    data = clientSocket.recv(1024)
    return data.decode()

# Just send terminal input to server
def send(message, clientSocket, isActive):
    # Inactive clients have already been disconnected and cannot send or receive
    if (isActive == False):
        return "inactive logout"
    
    # send message
    clientSocket.sendall(message.encode())

# Once a client is connected, authenticate the user at the very start
def loginUser(clientSocket):
    # Input a username
    message = input("Username:")
    user = message
    receivedMessage = sendAndReceive(message, clientSocket, True)
    
    # Username was found in credentials, prompt for password
    if (receivedMessage == "user exists"):
        message = input("Password:")
        receivedMessage = sendAndReceive(message, clientSocket, True)
        # Wrong PW, loop can be blocked by "welcome" or "blocked" message
        while (receivedMessage == "wrong pw"):
            print("Invalid Password. Please try again")
            message = input("Password:")
            receivedMessage = sendAndReceive(message, clientSocket, True)

    # Username not found in credentials, setup a new user and prompt for password
    elif (receivedMessage == "new user detected"):
        message = input("This is a new user. Enter a password:")
        receivedMessage = sendAndReceive(message, clientSocket, True)
        while (receivedMessage == "no spaces"):
            print("Password can't have spaces")
            message = input("Password:")
            receivedMessage = sendAndReceive(message, clientSocket, True)

    # ASSUMPTION: If the user had spaces in their name (multiple arguments)
    # restart the login process
    elif (receivedMessage == "multiple arguments"):
        print("Usernames can't have spaces, try again")
        return loginUser(clientSocket)
    
    # Cannot log into an account that's in use, restart login process
    elif receivedMessage == "in use":
        print("Account is already logged in with another client, please choose another")
        return loginUser(clientSocket)

    # Throwaway line acting as a 'continue', may refactor later
    elif (receivedMessage == "locked"):
        throwAway = True

    # At this stage the server has client down for signup or pw request
    # This would be an unknown state of neither, so shouldn't go to this line
    else:
        print("Serverside error: Unknown Login Response")
        sys.exit(1)

    # Authentication/Sign up stage complete! Welcome user and access board + retrieve timeoutPeriod
    if ("welcome user" in receivedMessage):
        print("Welcome to the greatest messaging application ever!")
        timeout = re.search("[0-9]*$", receivedMessage)
        timeout = int(timeout.group())
        return timeout, user
    # Or locked, in which case hold in the shadow realm
    # User can check if they are unlocked by sending to server
    elif (receivedMessage == "locked"):
        while (receivedMessage == "locked"):
            message = input("Invalid Password. Your account has been blocked. Please try again later")
            receivedMessage = sendAndReceive(message, clientSocket, True)
        # ReceivedMessage is no longer "blocked", can restart the login process
        print("No longer blocked, please restart the login process")
        return loginUser(clientSocket)
    else:
        print("Serverside error: Unknown Login Response")
        sys.exit(1)
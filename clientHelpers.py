from socket import *
import sys

# Sends client terminal input to server, and returns server response
def sendAndReceive(message, clientSocket):
    clientSocket.sendall(message.encode())
    data = clientSocket.recv(1024)
    return data.decode()

# Once a client is connected, authenticate the user at the very start
def loginUser(clientSocket):
    # Input a username
    message = input("Username:")
    receivedMessage = sendAndReceive(message, clientSocket)

    # Username was found in credentials, prompt for password
    if (receivedMessage == "user exists"):
        message = input("Password:")
        receivedMessage = sendAndReceive(message, clientSocket)
        # Wrong PW, loop can be blocked by "welcome" or "blocked" message
        while (receivedMessage == "wrong pw"):
            print("Invalid Password. Please try again")
            message = input("Password:")
            receivedMessage = sendAndReceive(message, clientSocket)

    # Username not found in credentials, setup a new user and prompt for password
    elif (receivedMessage == "new user detected"):
        message = input("This is a new user. Enter a password:")
        receivedMessage = sendAndReceive(message, clientSocket)
        while (receivedMessage == "no spaces"):
            message = input("Password can't have spaces")
            receivedMessage = sendAndReceive(message, clientSocket)

    # ASSUMPTION: If the user had spaces in their name (multiple arguments)
    # restart the login process
    elif (receivedMessage == "multiple arguments"):
        print("Usernames can't have spaces, try again")
        loginUser(clientSocket)
        return
        
    # At this stage the server has client down for signup or pw request
    # This would be an unknown state of neither, so shouldn't go to this line
    else:
        print("Serverside error: Unknown Login Response")
        sys.exit(1)

    # Authentication/Sign up stage complete! Welcome user and continue to board
    if (receivedMessage == "welcome user"):
        print("Welcome to the greatest messaging application ever!")
    # Or locked, in which case hold in the shadow realm
    # User can check if they are unlocked by sending to server
    elif (receivedMessage == "locked"):
        while (receivedMessage == "locked"):
            message = input("Invalid Password. Your account has been blocked. Please try again later")
            receivedMessage = sendAndReceive(message, clientSocket)
        # ReceivedMessage is no longer "blocked", can restart the login process
        print("No longer blocked, please restart the login process")
        loginUser(clientSocket)
        return
    else:
        print("Serverside error: Unknown Login Response")
        sys.exit(1)
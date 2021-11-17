from socket import *
import sys
import re
import datetime

# Sends message to client and returns the clients response
def sendAndReceive(message, clientSocket):
    print('[send] ' + message)
    clientSocket.send(message.encode())
    data = clientSocket.recv(1024)
    return data.decode()

def send(message, clientSocket):
    print('[send] ' + message)
    clientSocket.send(message.encode())

###### LOGIN HELPERS ######

# Returns a boolean over whether the username is in credentials.txt
def userInCredentials(user):
    f = open("credentials.txt", "r")
    lines = f.readlines()
    for line in lines:
        # Username is seperated by space
        userName = re.search("^.* ", line)
        userName = userName.group()
        # Remove tail space
        userName = userName[:-1]
        if userName == user:
            return True
    # Loop finished, haven't found user
    return False

# Similar to above method, but returns the users password
def getUserPassword(user):
    f = open("credentials.txt", "r")
    lines = f.readlines()
    for line in lines:
        # Username is seperated by space
        userName = re.search("^.* ", line)
        userName = userName.group()
        # Remove tail space
        userName = userName[:-1]
        if userName == user:
            password = re.search(" .*$", line)
            password = password.group()
            return password[1:]

# Registers user with given pw to credentials file
def registerUser(user, password):
    entry = "\n" + user + " " + password
    f = open("credentials.txt", "a")
    f.writelines(entry)

# Checks if a string has spaces, used to validify names and pw
def hasSpaces(str):
    if " " in str:
        return True
    else:
        return False

# Locks user
def lockUser(user, dict):
    dict[user] = datetime.datetime.now()
    return dict

# Checks if user is locked
def isLocked(user, dict, lockPeriod):
    if user not in dict:
        return False

    lockTime = dict[user]
    timePassed = datetime.datetime.now() - lockTime 
    print(timePassed)
    if timePassed.total_seconds() > lockPeriod:
        return False
    else:
        return True

###### USER LOG HELPERS ######

# Updates users last action in log when action is taken
def updUserLog(user, dict):
    dict[user] = datetime.datetime.now()
    return dict

# Checks if user has been active within a specified period (given in seconds)
def isActive(user, dict, activePeriod):
    if user not in dict:
        return False

    lastActive = dict[user]
    timePassed = datetime.datetime.now() - lastActive 
    print(timePassed)
    if timePassed.total_seconds() > activePeriod:
        return False
    else:
        return True
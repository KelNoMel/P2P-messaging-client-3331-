from socket import *
import sys
import re
import datetime

def sendAndReceive(message, clientSocket):
    print('[send] ' + message)
    clientSocket.send(message.encode())
    data = clientSocket.recv(1024)
    return data.decode()

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
# MIGHT NEED TO CHECK FOR NEWLINES
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

def registerUser(user, password):
    entry = user + " " + password
    f = open("credentials.txt", "a")
    f.writelines(entry)

def lockUser(user, dict):
    dict[user] = datetime.datetime.now()
    return dict

def isLocked(user, dict, lockPeriod):
    lockTime = dict[user]
    timePassed = datetime.datetime.now() - lockTime 
    print(timePassed)
    if timePassed.total_seconds() > lockPeriod:
        return False
    else:
        return True

def hasSpaces(str):
    if " " in str:
        return True
    else:
        return False



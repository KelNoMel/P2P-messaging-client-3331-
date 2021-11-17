from socket import *
import sys
import re
import datetime
from pathlib import Path

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

# Sets up the dictionary of lists required to store user information
# Used for offline messaging and block functionality
def dictListSetup():
    # Check if credentials exist and create file if it doesn't
    path = Path("credentials.txt")
    if not path.is_file():
        f = open("credentials.txt", "x")
        return {}

    # Otherwise, create a dictionary of lists for every known user in
    # credentials.txt
    newDict = {}
    f = open("credentials.txt", "r")
    lines = f.readlines()
    for line in lines:
        # Username is seperated by space
        userName = re.search("^.* ", line)
        userName = userName.group()
        # Remove tail space
        userName = userName[:-1]
        # Add entry in dict for user
        newDict[userName] = []
    return newDict

# Can be used to add new user to dictList or clear out entries
def dictListRefresh(user, dict):
    dict[user] = []

# Add an entry to dictList for user
def dictListAddEntry(user, dict, entry):
    if user not in dict:
        return False
    else:
        dict[user].append(entry)
        return True

# Remove an entry from user list
def dictListRemoveEntry(user, dict, entry):
    if user not in dict:
        return False
    elif entry not in dict[user]:
        return False
    else:
        dict[user].remove(entry)
        return True
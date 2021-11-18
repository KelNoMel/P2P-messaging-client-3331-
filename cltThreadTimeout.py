from threading import Thread
import time
from clientHelpers import sendAndReceive

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
        while self.isActive:
            t = time.time()

            if t >= self.timeoutDeadline:
                self.clientSocket.sendall("logout".encode())
                print("You have been logged out due to inactivity, press enter to continue")
                self.isInactive = False
                break

            time.sleep(sleep_seconds)

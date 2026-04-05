import threading
import os

class Audio():
    def __init__(self):
        pass

    def start_saying(self, type):
        thread = threading.Thread(target=self.say, args=(type, ))
        thread.start()

    def say(self, type):
        os.system(f'aplay ./assets/sentences/{type}.wav')


import time

class Task:

    def __init__(self, identify):
	self.identify = identify

    def start(self):
        time.sleep(2)
	print self.identify

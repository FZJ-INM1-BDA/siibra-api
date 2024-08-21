from threading import Timer

class RepeatTimer(Timer):
    """RepeatTimer
    
    runs `self.function` every `self.interval`
    """
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

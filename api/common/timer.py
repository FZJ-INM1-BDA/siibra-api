from threading import Timer
from typing import List, Callable

class RepeatTimer(Timer):
    """RepeatTimer
    
    runs `self.function` every `self.interval`
    """
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Cron:
    def __init__(self) -> None:
        self._minutely_fns: List[Callable] = []
        self._ten_minutely_fns: List[Callable] = []

        self._timers: List[RepeatTimer] = [
            RepeatTimer(60, self._run_minutely),
            RepeatTimer(600, self._run_ten_minutely)
        ]
    
    def _run_minutely(self):
        for fn in self._minutely_fns:
            fn()
    
    def _run_ten_minutely(self):
        for fn in self._ten_minutely_fns:
            fn()

    def minutely(self, fn: Callable):
        self._minutely_fns.append(fn)
        return fn

    def ten_minutely(self, fn: Callable):
        self._ten_minutely_fns.append(fn)
        return fn
    
    def run_all(self):
        self._run_ten_minutely()
        self._run_minutely()
    
    def start(self):
        for timer in self._timers:
            timer.start()
    
    def stop(self):
        """On terminate"""
        for timer in self._timers:
            timer.cancel()

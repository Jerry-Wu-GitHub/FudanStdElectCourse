r"""
encoding = "utf-8"
"""


from time import time

class Timer():
    """
    计时器类。
    """

    def __init__(self):
        self._time = time()
        self._paused = False
        self._pause_time = 0


    def pause(self):
        """
        暂停计时。
        """

        if not self._paused:
            self._paused = True
            self._pause_time = time()


    def start(self):
        """
        继续计时。
        """

        if self._paused:
            self._paused = False
            self._time += time() - self._pause_time


    def read(self, ndigits = 3):
        """
        读取经过的时间（秒）。
        """

        if self._paused:
            result = self._pause_time - self._time
        else:
            result = time() - self._time

        return round(result, ndigits)


    def reset(self):
        """
        将计时器归零。
        """

        self.set()


    def set(self, offset = 0):
        """
        将计时器设为`offset`。
        """

        self._time = time() - offset



if __name__ == "__main__":
    from time import sleep
    timer = Timer()
    print(timer.read())
    sleep(1)
    print(timer.read())
    timer.pause()
    sleep(1)
    print(timer.read())
    timer.start()
    sleep(1)
    print(timer.read())

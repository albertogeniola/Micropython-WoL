from ampy.files import Files
from ampy.pyboard import Pyboard
import time


class BoardSetup:
    board = None
    files = None

    def initialize(self, port):
        self.board = Pyboard(device=port, wait=10)
        self.files = Files(pyboard=self.board)
    
    def reset(self, seconds=1.0, wait=True):
        print("Waiting for REPL")
        self.board.enter_raw_repl()
        print("REPL acquired, issuing reset code")
        self.board.exec_(f'''
import machine\n
timer=machine.Timer(1)
def reset(*args, **kwargs):
    machine.reset()
timer.init(mode=machine.Timer.ONE_SHOT, period={int(seconds*1000)}, callback=reset)''')
        _board.board.exit_raw_repl()
        if wait:
            time.sleep(seconds)

_board = BoardSetup()
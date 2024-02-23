from machine import Pin, Timer
from buzzer import Buzzer
from constants import BUZZER_TIMER


class PassiveBuzzer(Buzzer):
    def __init__(self, *args, pin, **kwargs) -> None:
        super().__init__()
        self._beeping = False
        self.buzzer_pin = Pin(pin, Pin.OUT)
    
    def beep(self, long=False):
        if self._beeping:
            return
        
        self.buzzer_pin.value(1)

        timer = Timer(BUZZER_TIMER)
        timer.init(mode=Timer.ONE_SHOT, period=1000 if long else 500, callback=self._stop_beep)

    def _stop_beep(self, timer):
        self.buzzer_pin.value(0)
        timer.deinit()

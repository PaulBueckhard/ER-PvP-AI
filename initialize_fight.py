import pydirectinput
import time

class Initialize_Fight:
    def matchmaking(self):
        pydirectinput.press("e")
        time.sleep(0.5)
        pydirectinput.press("up")
        time.sleep(0.5)
        pydirectinput.press("e")
        time.sleep(0.5)
        pydirectinput.press("e")
        print("Started matchmaking")

    def lock_on(self):
        time.sleep(0.5)
        pydirectinput.press("q")
        time.sleep(0.1)
        print("Locked on to target")
        time.sleep(0.5)
        pydirectinput.press("r")

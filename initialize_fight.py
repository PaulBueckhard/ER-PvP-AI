import pydirectinput
import time
from colorama import Fore

class Initialize_Fight:
    def matchmaking():
        pydirectinput.press("e")
        time.sleep(0.5)
        pydirectinput.press("up")
        time.sleep(0.5)
        pydirectinput.press("e")
        time.sleep(0.5)
        pydirectinput.press("e")
        print(Fore.GREEN + "Started matchmaking")

    def lock_on():
        time.sleep(0.5)
        pydirectinput.press("q")
        time.sleep(0.1)
        print(Fore.GREEN + "Locked on to target")
        time.sleep(1.0)
        pydirectinput.press("r")

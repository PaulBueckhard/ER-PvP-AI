import cv2
import gym
import mss
import time
import numpy as np
from gym import spaces
import pydirectinput
import pytesseract
from colorama import Fore
from rewards import Rewards
from initialize_fight import Initialize_Fight

N_CHANNELS = 3
IMG_WIDTH = 1920
IMG_HEIGHT = 1080
MODEL_WIDTH = int(800 / 2)
MODEL_HEIGHT = int(450 / 2)

# List of actions
DISCRETE_ACTIONS = {
    "release_wasd": "release_wasd",
    "w": "forward",
    "a": "left",
    "s": "backward",
    "d": "right",
    "w+space": "forward_dodge",
    "a+space": "left_dodge",
    "s+space": "backward_dodge",
    "d+space": "right_dodge",
    "b": "light_attack",
    "n": "heavy_attack",
    "m": "powerstance_attack",
    "v": "skill",
    "w+b": "running_light",
    "w+n": "running_heavy",
    "w+m": "running_powerstance",
    "w+space+f+b": "jumping_light",
    "w+space+f+n": "jumping_heavy",
    "w+space+f+m": "jumping_powerstance",
    "x+b": "crouch_attack",
    "r": "use_item"
}

NUMBER_DISCRETE_ACTIONS = len(DISCRETE_ACTIONS)
NUM_ACTION_HISTORY = 10

class Environment(gym.Env):
    def __init__(self, config):

        # Set up environment
        super(Environment, self).__init__()

        # Set up gym spaces
        self.action_space = spaces.Discrete(NUMBER_DISCRETE_ACTIONS)
        spaces_dict = {
            "img": spaces.Box(low=0, high=255, shape=(MODEL_HEIGHT, MODEL_WIDTH, N_CHANNELS), dtype=np.uint8),
            "previous_actions": spaces.Box(low=0, high=1, shape=(NUM_ACTION_HISTORY, NUMBER_DISCRETE_ACTIONS, 1), dtype=np.uint8),
            "state": spaces.Box(low=0, high=1, shape=(2,), dtype=np.float32)
        }
        self.observation_space = gym.spaces.Dict(spaces_dict)

        # Set up variables
        pytesseract.pytesseract.tesseract_cmd = config["PYTESSERACT_PATH"]
        self.sct = mss.mss()
        self.reward = 0
        self.rewardGen = Rewards
        self.death = False
        self.duel_won = False
        self.t_start = time.time()
        self.done = False
        self.step_iteration = 0
        self.first_step = True
        self.max_reward = None
        self.reward_history = []
        self.action_history = []
        self.time_since_heal = time.time()
        self.action_name = ''
        self.MONITOR = config["MONITOR"]
        self.DEBUG_MODE = config["DEBUG_MODE"]
        self.GAME_MODE = config["GAME_MODE"]
        self.DESIRED_FPS = config["DESIRED_FPS"]

        self.init_fight = Initialize_Fight
        self.first_reset = True

    # One hot encoding of last 10 actions
    def one_hot_prev_actions(self, actions):
        oneHot = np.zeros(shape=(NUM_ACTION_HISTORY, NUMBER_DISCRETE_ACTIONS, 1))
        for i in range(NUM_ACTION_HISTORY):
            if len(actions) >= (i + 1):
                oneHot[i][actions[-(i + 1)]][0] = 1
        #print(oneHot)
        return oneHot
    
    # Grab screenshot of game
    def grab_screen_shot(self):
        monitor = self.sct.monitors[self.MONITOR]
        sct_img = self.sct.grab(monitor)
        frame = cv2.cvtColor(np.asarray(sct_img), cv2.COLOR_BGRA2RGB)
        frame = frame[46:IMG_HEIGHT + 46, 12:IMG_WIDTH + 12]
        if self.DEBUG_MODE:
            self.render_frame(frame)
        return frame
    
    # Render frame in debug mode
    def render_frame(self, frame):
        cv2.imshow('debug-render', frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()

    # Define actions that model can do
    def take_action(self, action):
        #action = -1 # Emergency block all actions
        if action == 0:
            pydirectinput.keyUp("w")
            pydirectinput.keyUp("s")
            pydirectinput.keyUp("a")
            pydirectinput.keyUp("d")
            self.action_name = "stop"
        elif action == 1:
            pydirectinput.keyUp("w")
            pydirectinput.keyUp("s")
            pydirectinput.keyDown("w")
            self.action_name = "w"
        elif action == 2:
            pydirectinput.keyUp("a")
            pydirectinput.keyUp("d")
            pydirectinput.keyDown("a")
            self.action_name = "a"
        elif action == 3:
            pydirectinput.keyUp("w")
            pydirectinput.keyUp("s")
            pydirectinput.keyDown("s")
            self.action_name = "s"
        elif action == 4:
            pydirectinput.keyUp("a")
            pydirectinput.keyUp("d")
            pydirectinput.keyDown("d")
            self.action_name = "d"
        elif action == 5:
            pydirectinput.keyDown("w")
            pydirectinput.press("space")
            self.action_name = "forward_dodge"
        elif action == 6:
            pydirectinput.keyDown("a")
            pydirectinput.press("space")
            self.action_name = "left_dodge"
        elif action == 7:
            pydirectinput.keyDown("s")
            pydirectinput.press("space")
            self.action_name = "backward_dodge"
        elif action == 8:
            pydirectinput.keyDown("d")
            pydirectinput.press("spadce")
            self.action_name = "right_dodge"
        elif action == 9:
            pydirectinput.press("b")
            self.action_name = "light_attack"
        elif action == 10:
            pydirectinput.press("n")
            self.action_name = "heavy_attack"
        elif action == 11:
            pydirectinput.press("m")
            self.action_name = "powerstance_attack"
        elif action == 12:
            pydirectinput.press("v")
            self.action_name = "skill"
        elif action == 13:
            pydirectinput.keyDown("space")
            pydirectinput.keyDown("w")
            time.sleep(0.35)
            pydirectinput.press("b")
            pydirectinput.keyUp("space")
            self.action_name = "running_light"
        elif action == 14:
            pydirectinput.keyDown("space")
            pydirectinput.keyDown("w")
            time.sleep(0.35)
            pydirectinput.press("n")
            pydirectinput.keyUp("space")
            self.action_name = "running_heavy"
        elif action == 15:
            pydirectinput.keyDown("space")
            pydirectinput.keyDown("w")
            time.sleep(0.35)
            pydirectinput.press("m")
            pydirectinput.keyUp("space")
            self.action_name = "running_powerstance"
        elif action == 16:
            pydirectinput.keyDown("space")
            pydirectinput.keyDown("w")
            time.sleep(0.2)
            pydirectinput.press("f")
            time.sleep(0.1)
            pydirectinput.press("b")
            pydirectinput.keyUp("space")
            self.action_name = "jumping_light"
        elif action == 17:
            pydirectinput.keyDown("space")
            pydirectinput.keyDown("w")
            time.sleep(0.2)
            pydirectinput.press("f")
            time.sleep(0.1)
            pydirectinput.press("n")
            pydirectinput.keyUp("space")
            self.action_name = "jumping_heavy"
        elif action == 18:
            pydirectinput.keyDown("space")
            pydirectinput.keyDown("w")
            time.sleep(0.2)
            pydirectinput.press("f")
            time.sleep(0.1)
            pydirectinput.press("m")
            pydirectinput.keyUp("space")
            self.action_name = "jumping_powerstance"
        elif action == 19:
            time.sleep(0.1)
            pydirectinput.press("x")
            time.sleep(0.2)
            pydirectinput.press("b")
            pydirectinput.press("x")
            self.action_name = "crouch_attack"

    # Wait for loading screen
    def wait_for_loading_screen(self):
        in_loading_screen = False
        have_been_in_loading_screen = False
        time_check_frozen_start = time.time()
        time_since_seen_next = None
        while True:
            frame = self.grab_screen_shot()
            in_loading_screen = self.check_for_loading_screen(frame)
            if in_loading_screen:
                print(Fore.GREEN + "Loading screen: ", in_loading_screen)
                have_been_in_loading_screen = True
                time_since_seen_next = time.time()
            else:
                if have_been_in_loading_screen:
                    print(Fore.GREEN + "Loading complete")
                else:
                    print(Fore.YELLOW + "Waiting for loading screen...")

            if have_been_in_loading_screen and (time.time() - time_since_seen_next) > 2.5:
                print(Fore.GREEN + "Left loading screen")
            elif have_been_in_loading_screen and ((time.time() - time_check_frozen_start) > 90):
                print(Fore.RED + "Did not leave loading screen. Game likely frozen.")
                exit()
            elif not have_been_in_loading_screen and ((time.time() - time_check_frozen_start) > 20):
                print(Fore.RED + "No loading screen detected")
                time_check_frozen_start = time.time()

    def check_for_loading_screen(self, frame):
        next_text_image = frame[975:1010, 135:195]
        next_text_image = cv2.resize(next_text_image, ((205-155)*3, (1040-1015)*3))
        lower = np.array([0,0,75])
        upper = np.array([255,255,255])
        hsv = cv2.cvtColor(next_text_image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        pytesseract_output = pytesseract.image_to_string(mask,  lang='eng',config='--psm 6 --oem 3')
        in_loading_screen = "Next" in pytesseract_output or "next" in pytesseract_output

        if self.DEBUG_MODE:
            matches = np.argwhere(mask==255)
            percent_match = len(matches) / (mask.shape[0] * mask.shape[1])
            print(percent_match)

        return in_loading_screen
    
    # Step function called by train
    def step(self, action):
        if self.first_step:
            print(Fore.CYAN + "Initiated first step")
        time_start = time.time()
        frame = self.grab_screen_shot()
        self.reward, self.death, self.duel_won = self.rewardGen.update(frame, self.first_step)

        if self.DEBUG_MODE:
            print(Fore.CYAN + "Reward: ", self.reward)
            print(Fore.CYAN + "Death: ", self.death)

        # Check if game is done
        if self.death:
            self.done = True
            print(Fore.CYAN + "Player died")
        if self.duel_won:
            self.done = True
            print(Fore.CYAN + "Duel won!")

        # Take action
        if not self.done:
            self.take_action(action)

        # Return values
        info = {}
        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        if self.DEBUG_MODE: self.render_frame(observation)
        if self.max_reward is None:
            self.max_reward = self.reward
        elif self.max_reward < self.reward:
            self.max_reward = self.reward
        self.reward_history.append(self.reward)
        spaces_dict = {
            'img': observation,
            'previous_actions': self.one_hot_prev_actions(self.action_history),
            'state': np.asarray([self.rewardGen.current_hp, self.rewardGen.current_stamina])
        }

        # Update variables
        self.first_step = False
        self.step_iteration += 1
        self.action_history.append(int(action))

        # Limit FPS
        time_end = time.time()
        desired_FPS = (1 / self.DESIRED_FPS)
        time_to_sleep = desired_FPS - (time_end - time_start)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)

        current_fps = str(round(((1 / ((time_end - time_start) * 10)) * 10), 1))

        # Console ouput of step
        if not self.done:
            self.reward = round(self.reward, 0)
            reward_with_spaces = str(self.reward)
            for i in range(5 - len(reward_with_spaces)):
                reward_with_spaces = " " + reward_with_spaces
            max_reward_with_spaces = str(self.max_reward)
            for i in range(5 - len(max_reward_with_spaces)):
                max_reward_with_spaces = " " + max_reward_with_spaces
            for i in range(18 - len(str(self.action_name))):
                self.action_name = " " + self.action_name
            for i in range(5 - len(current_fps)):
                current_fps = " " + current_fps
            print("Iteration: " + str(self.step_iteration) + "| FPS: " + current_fps + "| Reward: " + reward_with_spaces + "| Max Reward: " + max_reward_with_spaces + "| Action: " + str(self.action_name))
        else:
            print("Reward: " + str(self.reward) + "| Max Reward: " + str(self.max_reward))

        # Return observation
        return spaces_dict, self.reward, self.done, info
    
    # Reset function
    def reset(self):
        print(Fore.YELLOW + "Resetting...")

        self.take_action(0)
        print(Fore.YELLOW + "Releasing keys")

        # Print average reward
        if len(self.reward_history) > 0:
            total_reward = 0
            for reward in self.reward_history:
                total_reward += reward
            average_reward = total_reward / len(self.reward_history)
            print(Fore.CYAN + "Average reward of prior run: ", average_reward)

        # Check for loading screen
        if not self.first_reset:
            self.wait_for_loading_screen()
            self.init_fight.matchmaking()
        self.first_reset = False
        self.wait_for_loading_screen()
        self.init_fight.lock_on()

        # Reset all variables
        self.step_iteration = 0
        self.reward_history = [] 
        self.done = False
        self.first_step = True
        self.max_reward = None
        self.rewardGen.previous_hp = 1
        self.rewardGen.current_hp = 1
        self.rewardGen.time_since_dmg_taken = time.time()
        self.action_history = []
        self.time_start = time.time()

        # Return first observation
        frame = self.grab_screen_shot()
        observation = cv2.resize(frame, (MODEL_WIDTH, MODEL_HEIGHT))
        spaces_dict = {
            "img": observation,
            "previous_actions": self.one_hot_prev_actions(self.action_history),
            "state": np.asarray([1.0, 1.0])
        }

        print(Fore.GREEN + "Finished reset")
        return spaces_dict

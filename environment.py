import cv2
import gym
import mss
import time
import numpy as np
from gym import spaces
import pydirectinput
import pytesseract
from rewards import Rewards

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
            "prev_actions": spaces.Box(low=0, high=1, shape=(NUM_ACTION_HISTORY, NUMBER_DISCRETE_ACTIONS, 1), dtype=np.uint8),
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

        self.matchmaking = None
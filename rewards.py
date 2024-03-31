import cv2
import numpy as np
import time
import pytesseract

class Rewards:
    # Constructor
    def __init__(self, config):
        pytesseract.pytesseract.tesseract_cmd = config["PYTESSERACT_PATH"]
        self.GAME_MODE = config["GAME_MODE"]
        self.DEBUG_MODE = config["DEBUG_MODE"]
        self.max_hp = config["PLAYER_HP"]
        self.previous_hp = 1.0
        self.current_hp = 1.0
        self.time_since_dmg_taken = time.time()
        self.death = False
        self.max_stam = config["PLAYER_STAMINA"]
        self.current_stamina = 1.0
        self.time_since_opponent_damaged = time.time()
        self.time_alive = time.time()  
        self.game_won = False    
        self.image_detection_tolerance = 0.02

    # Detect current player HP
    def get_current_hp(self, frame):
        HP_RATIO = 0.403
        hp_image = frame[51:53, 155:155 + int(self.max_hp * HP_RATIO) - 20]
        
        if self.DEBUG_MODE: 
            self.render_frame(hp_image)

        lower = np.array([0,90,75])
        upper = np.array([150,255,125])
        hsv = cv2.cvtColor(hp_image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        if self.DEBUG_MODE: self.render_frame(mask)

        matches = np.argwhere(mask==255)
        current_hp = len(matches) / (hp_image.shape[1] * hp_image.shape[0])

        current_hp += 0.02
        if current_hp >= 0.95:
            current_hp = 1.0

        if self.DEBUG_MODE:
            print("Current HP: ", current_hp)
        
        return current_hp
    
    # Detect current player stamina
    def get_current_stamina(self, frame):
        STAMINA_RATIO = 3.0
        stamina_image = frame[86:89, 155:155 + int(self.max_stam * STAMINA_RATIO) - 20]
        
        if self.DEBUG_MODE:
            self.render_frame(stamina_image)

        lower = np.array([6,52,24])
        upper = np.array([74,255,77])
        hsv = cv2.cvtColor(stamina_image, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
       
        if self.DEBUG_MODE:
            self.render_frame(mask)

        matches = np.argwhere(mask==255)
        self.current_stamina = len(matches) / (stamina_image.shape[1] * stamina_image.shape[0])

        self.current_stamina += 0.02
        if self.current_stamina >= 0.95:
            self.current_stamina = 1.0

        if self.DEBUG_MODE:
            print("Current stamina: ", self.current_stamina)

        return self.current_stamina
    
    # Detect if opponent is damaged
    def detect_opponent_damaged(self, frame):
        cut_frame = frame[150:400, 350:1700]

        lower = np.array([24,210,0])
        upper = np.array([25,255,255])
        hsv = cv2.cvtColor(cut_frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        matches = np.argwhere(mask==255)
        if len(matches) > 30:
            return True
        else:
            return False
        
    # Detect if duel is won
    def detect_win(self, frame):
        cut_frame = frame[730:800, 550:1350]
        lower = np.array([0,0,75])
        upper = np.array([255,255,255])
        hsv = cv2.cvtColor(cut_frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        pytesseract_output = pytesseract.image_to_string(mask,  lang='eng',config='--psm 6 --oem 3')
        game_won = "Combat ends in your victory!" in pytesseract_output or "combat ends in your victory!" in pytesseract_output
        return game_won
    
    # Debug function
    def render_frame(self, frame):
        cv2.imshow("debug-render", frame)
        cv2.waitKey(1000)
        cv2.destroyAllWindows()

    # Update function returning reward
    def update(self, frame, first_step):
        # Getting current values
        self.current_hp = self.get_current_hp(frame)                   
        self.current_stam = self.get_current_stamina(frame)            
        if first_step: self.time_since_dmg_taken = time.time() - 10

        self.death = False
        if self.current_hp <= 0.01 + self.image_detection_tolerance:
            self.death = True
            self.current_hp = 0.0

        # HP rewards
        hp_reward = 0
        if not self.death:
            if self.current_hp < self.previous_hp - self.image_detection_tolerance:
                hp_reward = -75
                self.time_since_dmg_taken = time.time()
        else:
            hp_reward = -500

        time_since_taken_dmg_reward = 0
        if time.time() - self.time_since_dmg_taken > 5:
            time_since_taken_dmg_reward = 25

        self.previous_hp = self.current_hp

        # Fighting rewards
        fight_reward = 0
        enemy_damaged = self.detect_opponent_damaged(frame)
        if enemy_damaged:
            fight_reward = 75
            self.time_since_opponent_damaged = time.time()
        else:
            if time.time() - self.time_since_opponent_damaged > 5:
                fight_reward = -25
            else:
                fight_reward = 0

        # Win reward
        self.game_won = self.detect_win(frame)
        if self.game_won:
            fight_reward = 500

        # Return total reward
        total_reward = hp_reward + time_since_taken_dmg_reward + fight_reward
        total_reward = round(total_reward, 3)

        return total_reward, self.death, self.game_won
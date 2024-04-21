# Elden AI
Elden AI is a Machine Learning project designed to train a Reinforcement Learning agent to compete in PvP (player versus player) matches in Elden Ring. The project utilizes [computer vision](https://pypi.org/project/opencv-python/) to interpret the game state, [OpenAI's gym](https://github.com/openai/gym) to generate a learning environment, and simulates [keypresses](https://pypi.org/project/PyDirectInput/) to interact with the game. 

## Setup
Clone the repository:

    $ git clone https://github.com/PaulBueckhard/ER-PvP-AI.git
    
Install dependencies:

    $ pip install -r requirements.txt

Download Tesseract-OCR.
Change the following in-game controls in Elden Ring:
 - Attack: B
 - Strong Attack: N
 - Guard: M
 - Skill: V
 
Set the game to windowed mode in 1920x1080 resolution. Do not move the window from its initial position.

In main.py, adjust the environment configuration:
 - Set the path your tesseract.exe
 - Set which monitor the game is running on
 - Adjust PLAYER_HP and PLAYER_STAMINA to the stats of your character

## Train model
If everything is set up correctly, position your in-game character in front of the colosseum statue in Roundtable Hold. Run main.py and search for a duel in Limgrave. The code will then start a training session automatically. The program will output its state in the console and will inform you of each iteration, action and reward. After 500 iterations (about 20 duels) the model will be saved.

When a model is newly created, all actions will be purely random. It will update its behavior once a model has been saved.


## Architecture
### Environment
The environment module is responsible for setting up the game environment for the RL agent. It captures game frames, preprocesses the images, and defines the action and observation spaces.
**Key components:**
 - **Observation space**
	 - **Game screen:** captures current game screen in an image
	 - **Previous actions:** captures the last 10 actions the agent took
 - **Action Space**
	 - **Available actions:** Defines the actions the agent is able to take

### Rewards
The rewards module calculates the rewards for the RL agent based on the current game state. It analyzes the player's health points (HP), stamina, opponent's damage, and determines whether the player has won or lost the duel.
**Key components:**
 - **HP detection**
	 - **HP region:** Analyzes the region of the game frame to detect the player's current HP
	 - **Detection method:** Uses color thresholding to determine the percentage of red pixels in HP bar
	 - **Loss detection:** Determines if the player has died if amount of HP goes beneath certain threshold
 - **Stamina detection**
	 - **Stamina region:** Analyzes the region of the game frame to detect the player's current stamina
	 - **Detection method:** Uses color thresholding to determine the percentage of green pixels in stamina bar
 - **Opponent Damage detection**
	 - Since the HP bar of opponents is constantly moving, the code analyzes the region the opponent's HP bar can appear at and looks for the specific yellow color that appears, when an opponent is damaged.
 - **Win detection**
	- **Win Region**: Scans a specific region to detect victory text
	- **Detection Method**: Utilizes optical character recognition (OCR) using pytesseract to identify victory text

### Hardcoded actions
The initialize_fight module handles the initialization of the fight by simulating keypresses to start the matchmaking process and lock onto the opponent.
**Key Components**
- **Matchmaking**:
    - **Keypresses**: Simulates key presses to search for a duel at the colosseum statue
- **Lock On**:
    - **Keypresses**: Simulates keypresses to lock onto a target and navigates the emote menu to greet the opponent

## Video demonstration
Here is a video demonstration of a model that has been trained for 10 hours:
https://youtu.be/Avk-r0KG5Ik
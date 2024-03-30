from stable_baselines3 import PPO, A2C
import os
from environment import Environment

def train(CREATE_NEW_MODEL, config):
    print("Training initialized")

    TIMESTEPS = 1
    HORIZON_WINDOW = 500

    # Creating folder structure
    model_name = "PPO-1" 					
    if not os.path.exists(f"models/{model_name}/"):
        os.makedirs(f"models/{model_name}/")
    if not os.path.exists(f"logs/{model_name}/"):
        os.makedirs(f"logs/{model_name}/")
    models_dir = f"models/{model_name}/"
    logdir = f"logs/{model_name}/"			
    model_path = f"{models_dir}/PPO-1"
    print("Created folder structure")


    # Initialize environment
    env = Environment(config)
    print("Initialized environment")
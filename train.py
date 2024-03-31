from stable_baselines3 import PPO, A2C
import os
from colorama import Fore
from environment import Environment

def train(CREATE_NEW_MODEL, config):
    print(Fore.GREEN + "Training initialized")

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
    print(Fore.GREEN + "Created folder structure")


    # Initialize environment
    env = Environment(config)
    print(Fore.GREEN + "Initialized environment")

    # Create new model or load existing model
    if CREATE_NEW_MODEL:
        model = PPO(
            "MultiInputPolicy",
            env,
            tensorboard_log=logdir,
            n_steps=HORIZON_WINDOW,
            verbose=1,
            device="cpu"
            )
        print(Fore.GREEN + "Created new model...")
    else:
        model = PPO.load(model_path, env=env)
        print(Fore.GREEN + "Loaded model...")

    # Training loop
    while True:
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO", log_interval=1)
        model.save(f"{models_dir}/PPO-1")
        print(Fore.GREEN + "Updated model...")
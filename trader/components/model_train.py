import gymnasium as gym
import gym_anytrading
from trader.utils.logger import logging
from trader.components.stockenv import StockEnvironment
import os
import pandas as pd

from gym_anytrading.envs import StocksEnv
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO


from trader.config import ConfigManager

class Agent:
    def __init__(self,config: ConfigManager):
        self.data_config = config.get_data_config()
        self.model_config = config.get_model_config()

    def train(self):

        lookback_window_size = self.model_config.lookback
        time_steps = self.model_config.time_steps
        model_name = self.model_config.model_file
        
      

        stacked_df = pd.read_csv( self.data_config.processed_data_file)
    

        env = StockEnvironment(df=stacked_df,window_size=lookback_window_size,frame_bound=(lookback_window_size,stacked_df.shape[0]))
        logging.info(f"Train environment created with df shape: {env.df.shape}, observation space: {env.observation_space.shape}, action space: {env.action_space.n}")


        model = PPO('MlpPolicy',
                    env=env,
                    learning_rate=3e-4,
                    verbose=1,
                    n_steps=2048,
                    batch_size=256,
                    n_epochs=20,
                    gamma=0.999,
                    clip_range=0.2,
                    ent_coef=0.0001,
                    # vf_coef=0.5,
                    policy_kwargs=dict(
                    net_arch=[64, 64],  # Larger network architecture for complex environments
                    ),            
                    # learning_rate=linear_schedule(3e-4), 
                    )
        # if os.path.exists(os.path.join(MODEL_SAVE_DIR,model_name,'zip')):
        #     model = model.load(os.path.join(MODEL_SAVE_DIR,model_name,'zip'))
        #     logging.info("Model loaded successfully")
        # else:
            # logging.info("Model not found, training new model")
        model.learn(total_timesteps=time_steps,)

        os.makedirs(os.path.dirname(model_name),exist_ok=True)
        model.save(model_name)

        # observation = env.reset()
        # while True:
        #     action = env.action_space.sample()
        #     observation, reward, done, info = env.step(action)
        #     if done:
        #         print("info:", info)
        #         break

        # env.render()
        # env.close()
    def linear_schedule(initial_value):
        """
        Linear learning rate schedule.
        :param initial_value: Initial learning rate.
        :return: schedule that computes current learning rate depending on progress
        """
        def func(progress_remaining):
            return progress_remaining * initial_value
        return func

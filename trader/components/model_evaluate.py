
from trader.utils.logger import logging
from trader.components.stockenv import StockEnvironment
import os
import pandas as pd


from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
import matplotlib.pyplot as plt

import mlflow
import dagshub


from trader.config import ConfigManager

class Evaluation:
    def __init__(self,config: ConfigManager):
        self.data_config = config.get_data_config()
        self.model_config = config.get_model_config()
        dagshub.init(repo_owner='me1402utsa', repo_name='ML_trading', mlflow=True)

    def eval(self):

        lookback_window_size = self.model_config.lookback
        stacked_df = pd.read_csv( self.data_config.processed_data_file)
        env = StockEnvironment(df=stacked_df,window_size=lookback_window_size,frame_bound=(lookback_window_size,stacked_df.shape[0]))
        logging.info(f"Test environment created with df shape: {env.df.shape}, observation space: {env.observation_space.shape}, action space: {env.action_space.n}")


        model = PPO('MlpPolicy',
                    env=env,
                    )
        
        if os.path.exists(self.model_config.model_file):
            model = model.load(self.model_config.model_file)
            logging.info("Model loaded successfully")
        else:
            logging.info("Model not found")
            raise Exception("Model not found")
        
        with mlflow.start_run():
            self.rl_eval(env,model)
            self.buy_hold_eval(env)
            self.random_eval(env)

    def rl_eval(self,env,model):
        observation,_ = env.reset()
        while True:
            action,_ = model.predict(observation, deterministic=True)
            observation, reward,_, done, info = env.step(action)
            if done:
                break
        print(f"RL optimized {info['total_profit']}, Reward {info['total_reward']}")
        print(f"Max possible profit: {env.max_possible_profit()}")

        mlflow.log_metric("rl_profit",info['total_profit'])

        
        plt.figure(figsize=(15,6))
        plt.cla()
        env.render_all()
        plt_path = "artifacts/plots/test.png"
        os.makedirs(os.path.dirname(plt_path),exist_ok=True)
        plt.savefig(plt_path)
        plt.close()
        mlflow.log_artifact(plt_path)
        mlflow.log_params(self.data_config.__dict__)
        mlflow.log_params(self.model_config.__dict__)

    def buy_hold_eval(self,env):
        observation,_ = env.reset()
        while True:
            action = 1
            observation, reward,_, done, info = env.step(action)
            if done:
                break
        print(f"buy and hold profit: {info['total_profit']}, Reward {info['total_reward']}")
        mlflow.log_metric("buy_hold_profit",info['total_profit'])

    def random_eval(self,env):
        observation,_ = env.reset()
        while True:
            action = env.action_space.sample()
            observation, reward,_, done, info = env.step(action)
            if done:
                break
        print(f"Random profit: {info['total_profit']}, Reward {info['total_reward']}")
        mlflow.log_metric("random_profit",info['total_profit'])

import gymnasium as gym
import gym_anytrading
from trader_bot.config import DATA_SAVE_DIR, MODEL_SAVE_DIR
from trader_bot.utils.logger import logging
from trader_bot.meta.stockenv import StockEnvironment
import os
import pandas as pd

from gym_anytrading.envs import StocksEnv
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
import matplotlib.pyplot as plt


def test(lookback_window_size=5,model_name="ppo"):

    stacked_df = pd.read_csv( os.path.join(DATA_SAVE_DIR,"data_test.csv")   )
    # stacked_df = pd.read_csv( os.path.join(DATA_SAVE_DIR,"data_train.csv"))

    # patterns = ['volume', 'close', 'rsi']
    # # Combine patterns into a single regular expression
    # regex_pattern = '|'.join(patterns)
    # # Filter columns based on the combined pattern
    # regex_pattern = '^(' + '|'.join(patterns) + ')'
    # # Filter columns based on the combined pattern
    # selected_columns = stacked_df.filter(regex=regex_pattern)
    # logging.info(f"Load data with selected features: {selected_columns.columns}")
    

    env = StockEnvironment(df=stacked_df,window_size=lookback_window_size,frame_bound=(lookback_window_size,stacked_df.shape[0]))
    logging.info(f"Test environment created with df shape: {env.df.shape}, observation space: {env.observation_space.shape}, action space: {env.action_space.n}")


    model = PPO('MlpPolicy',
                env=env,
                # learning_rate=3e-4,
                # verbose=1,
                # n_steps=2048,
                # batch_size=64,
                # n_epochs=10,
                # gamma=0.99,
                # clip_range=0.2,
                # ent_coef=0.01,
                # vf_coef=0.5,
                
                # # learning_rate=linear_schedule(1e-4), 
                )
    print(os.path.join(MODEL_SAVE_DIR,model_name,'zip'))
    if os.path.exists(os.path.join(MODEL_SAVE_DIR,f"{model_name}.zip")):
        model = model.load(os.path.join(MODEL_SAVE_DIR,model_name))
        logging.info("Model loaded successfully")
    else:
        logging.info("Model not found")
        raise Exception("Model not found")


    observation,_ = env.reset()
    while True:
        # action = env.action_space.sample()
        action,_ = model.predict(observation, deterministic=False)
        # action = 0
        observation, reward,_, done, info = env.step(action)
        # env.render()
        if done:
            print("info:", info)
            break
    print(f"RL optimized {info['total_profit']}, Reward {info['total_reward']}")
    print(f"Max possible profit: {env.max_possible_profit()}")

    plt.figure(figsize=(15,6))
    plt.cla()
    env.render_all()
    plt.savefig("test.png")

    observation,_ = env.reset()
    while True:
        # action = env.action_space.sample()
        # action,_ = model.predict(observation, deterministic=True)
        action = 1
        observation, reward,_, done, info = env.step(action)
        # env.render()
        if done:
            break
    print(f"buy and hold profit: {info['total_profit']}, Reward {info['total_reward']}")

    observation,_ = env.reset()
    while True:
        action = env.action_space.sample()
        # action,_ = model.predict(observation, deterministic=True)
        # action = 1
        observation, reward,_, done, info = env.step(action)
        # env.render()
        if done:
            break
    print(f"Random profit: {info['total_profit']}, Reward {info['total_reward']}")

if __name__ == "__main__":

    from trader_bot.train import train
    from trader_bot.config_tickers import DOW_30_TICKER

    # from trader_bot.meta.alpaca_processor import DataIngestion
    # ticker_list = ['SPY']+DOW_30_TICKER
    # data_ingestion=DataIngestion(start='2024-05-01',end='2024-07-01',interval = '1Day',ticker_list = ticker_list)
    # data=data_ingestion.initiate(train=True)

    # data_ingestion=DataIngestion(start='2024-07-01',end='2024-09-01',interval = '1Day',ticker_list = ticker_list)
    # data=data_ingestion.initiate(train=False)

    # lookback=5
    # model="ppo"
    # train(lookback_window_size=lookback,time_steps=200000,model_name=model)
    # test(lookback_window_size=lookback,model_name=model)


    from trader_bot.meta.alpaca_processor_minute import DataIngestion
    ticker_list = ['SPY']+DOW_30_TICKER
    # data_ingestion=DataIngestion(start='2024-08-01',end='2024-09-01',interval = '1Min',ticker_list = ticker_list)
    # data=data_ingestion.initiate(train=True)

    data_ingestion=DataIngestion(start='2024-07-01',end='2024-07-07',interval = '1Min',ticker_list = ticker_list)
    data=data_ingestion.initiate(train=False)

    lookback=15
    model="ppo_minute"
    # train(lookback_window_size=lookback,time_steps=200000,model_name=model)
    test(lookback_window_size=lookback,model_name=model)
# ML-based Trading bot

- Trade SPY at daily or minute intervals with the goal of outperforming the buy-and-hold strategy.

- Trading algorithms: PPO 

- Deployment: CI/CD pipeline implemented with GitHub Actions on a self-hosted runner (RTX 3090).

- Key performance factors:
    - Lookback window size
    - Indicators
    - Training data period
    - Trading intervals



### Trained with 30-day lookback window
|  | Buy&Hold     | Max possible     | RL optimized     | Profit increase|
|--------------|--------------|--------------|--------------|--------------|
| **Train** (2023-01-01 to 2023-12-31)| 1.16| 1.99| 1.42|  **22%**|
| **Test1** (2024-01-01 to 2024-09-01) | 1.11| 1.59| 1.17| **5%**|
| **Test2** (2022-01-01 to 2022-12-31) | 0.86| 2.99| 0.92| **7%**|
<!-- <div style="display: flex; flex-direction: column; align-items: center;">
    <img src="artifacts/plots/train.png" alt="Plot 1" style="margin-bottom: 20px;" />
    <img src="artifacts/plots/test1.png" alt="Plot 2" />
    <img src="artifacts/plots/test.png" alt="Plot 2" />
</div> -->


### Training Results
The plot below represents the training phase, where red indicates a short position and green signifies a hold position.

<p align="center"> <img src="artifacts/plots/train.png" alt="Training Results" width="700" height="300"> </p>


### Test 1 Results
This plot displays the results for the first test period.

<p align="center"> <img src="artifacts/plots/test1.png" alt="Test 1 Results" width="700" height="300"> </p>


### Test 2 Results
The plot below shows the results for the second test period.

<p align="center"> <img src="artifacts/plots/test.png" alt="Test 2 Results" width="700" height="300"> </p>
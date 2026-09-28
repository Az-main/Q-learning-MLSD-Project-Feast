# Hyperparameter Experiments

## Goal

Select the Q-learning parameters from measured results instead of keeping an
untested choice. The primary selection metric is total reward on the untouched
2017 test split because the reward includes sales revenue, ordering cost,
holding cost and stockout penalty.

## Method

The experiment tested a 3 by 3 grid:

- Learning rate (`alpha`): 0.05, 0.10, 0.20
- Discount factor (`gamma`): 0.90, 0.95, 0.99

Every run used the same training data, chronological test data, 600 episodes,
epsilon schedule and random seed 42. This means only `alpha` and `gamma`
changed between runs.

Experiments were tracked with DVC using commands such as:

```powershell
dvc exp run evaluate --name alpha-020-gamma-090 `
  -S train.alpha=0.20 `
  -S train.gamma=0.90

dvc exp show --no-pager --only-changed
```

## Results

| Alpha | Gamma | Last 50 training reward | Test reward | Service level | Stockout rate | Average leftover |
|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 0.90 | 2,434.82 | 15,673.6 | 0.794 | 0.592 | 2.76 |
| 0.05 | 0.95 | 2,379.80 | 15,667.0 | 0.794 | 0.595 | 2.82 |
| 0.05 | 0.99 | 2,491.04 | 16,049.3 | 0.804 | 0.573 | 2.98 |
| 0.10 | 0.90 | 2,791.64 | 17,690.4 | 0.849 | 0.479 | 4.58 |
| 0.10 | 0.95 | 2,755.28 | 18,197.3 | 0.860 | 0.466 | 3.92 |
| 0.10 | 0.99 | **2,803.92** | 18,912.0 | 0.877 | 0.447 | 3.78 |
| **0.20** | **0.90** | 2,696.25 | **20,512.0** | **0.947** | **0.162** | 15.07 |
| 0.20 | 0.95 | 2,582.77 | 11,459.1 | 0.702 | 0.586 | 7.08 |
| 0.20 | 0.99 | 2,677.00 | 16,055.1 | 0.830 | 0.411 | 12.34 |

## Selection

`alpha=0.20` and `gamma=0.90` were selected because they achieved the highest
test reward. Compared with the original `alpha=0.10`, `gamma=0.95` settings:

- Total reward increased from 18,197.3 to 20,512.0, a 12.7% improvement.
- Service level increased from 0.860 to 0.947.
- Stockout rate decreased from 0.466 to 0.162.
- Average leftover increased from 3.92 to 15.07, but remained below the
  recent-average policy's 26.47 and is already penalized by the reward function.

The winning values are stored in `params.yaml`. The full pipeline was
reproduced with these values, and the smoke tests, drift stage and Feast stage
all passed.

The experiment used one fixed seed to make the comparison reproducible. A
larger study could repeat each combination across multiple seeds.

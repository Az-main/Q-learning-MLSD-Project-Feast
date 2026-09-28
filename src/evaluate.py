"""Evaluate the trained policy against simple baselines."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from agent import QLearningAgent
from env import InventoryEnv
from utils import ROOT, load_params, save_json


def run_policy(env: InventoryEnv, choose) -> dict:
    """Run one policy over the complete test split."""
    state = env.reset()
    total = demand = sold = leftover = 0.0
    stockout_days, days, done = 0, 0, False
    while not done:
        action = choose(state, env)
        state, reward, done, info = env.step(action)
        total += reward
        demand += info["demand"]
        sold += info["sold"]
        leftover += info["leftover"]
        stockout_days += int(info["unmet"] > 0)
        days += 1
    return {
        "total_reward": round(float(total), 1),
        "service_level": round(float(sold / demand), 3),
        "stockout_rate": round(float(stockout_days / days), 3),
        "avg_leftover": round(float(leftover / days), 2),
    }


def main() -> None:
    params = load_params()
    ep = params["env"]
    actions = ep["actions"]
    data = pd.read_parquet(ROOT / "data" / "processed" / "test.parquet")
    env = InventoryEnv(data, ep)

    agent = QLearningAgent(len(actions), alpha=0, gamma=0, epsilon=0.0)
    agent.load(ROOT / "models" / "q_table.json")
    rng = np.random.default_rng(0)
    rolling = data["rolling_demand"].to_numpy()

    policies = {
        "q_learning": lambda s, e: agent.act(s),
        "random": lambda s, e: int(rng.integers(len(actions))),
        "always_order_20": lambda s, e: actions.index(20),
        "order_recent_avg": lambda s, e: int(np.argmin([abs(a - rolling[e.t]) for a in actions])),
    }
    results = {name: run_policy(env, fn) for name, fn in policies.items()}
    save_json(results, ROOT / "metrics" / "eval.json")

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    names = list(results)
    values = [results[n]["total_reward"] for n in names]
    colors = ["tab:green" if n == "q_learning" else "tab:gray" for n in names]
    plt.figure(figsize=(7, 4))
    plt.bar(names, values, color=colors)
    plt.ylabel("Total reward on test year")
    plt.title("Q-learning vs baseline policies")
    plt.tight_layout()
    plt.savefig(out / "policy_comparison.png", dpi=120)
    plt.close()

    for name, r in results.items():
        print(f"{name:18s} {r}")


if __name__ == "__main__":
    main()

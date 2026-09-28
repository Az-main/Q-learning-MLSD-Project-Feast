"""Inventory simulator with overnight order delivery."""

import numpy as np
import pandas as pd


class InventoryEnv:
    def __init__(self, data: pd.DataFrame, env_params: dict):
        self.demand = data["demand"].to_numpy()
        self.dow = data["day_of_week"].to_numpy()
        self.trend = data["demand_trend"].to_numpy()
        self.p = env_params
        self.actions = env_params["actions"]
        self.n_days = len(data)

    def state(self) -> tuple:
        stock_bucket = int(np.digitize(self.stock, self.p["stock_bins"]))
        return (stock_bucket, int(self.dow[self.t]), int(self.trend[self.t]))

    def reset(self, start: int = 0, length: int | None = None) -> tuple:
        """Start an episode at the requested row."""
        self.t = start
        self.end = self.n_days if length is None else min(start + length, self.n_days)
        self.stock = self.p["initial_stock"]
        return self.state()

    def step(self, action_index: int):
        p = self.p
        order = self.actions[action_index]
        demand = self.demand[self.t]

        sold = min(self.stock, demand)
        unmet = demand - sold
        leftover = self.stock - sold

        reward = (p["price"] * sold
                  - p["order_cost"] * order
                  - p["holding_cost"] * leftover
                  - p["stockout_penalty"] * unmet)

        self.stock = min(p["capacity"], leftover + order)
        self.t += 1
        done = self.t >= self.end

        info = {"demand": demand, "sold": sold, "unmet": unmet,
                "leftover": leftover, "order": order}
        next_state = None if done else self.state()
        return next_state, float(reward), done, info

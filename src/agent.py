"""Tabular Q-learning agent with epsilon-greedy exploration."""

import numpy as np

from utils import load_json, save_json

N_STOCK, N_DOW, N_TREND = 8, 7, 3


class QLearningAgent:
    def __init__(self, n_actions: int, alpha: float, gamma: float,
                 epsilon: float, seed: int = 0):
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = np.random.default_rng(seed)
        self.q = np.zeros((N_STOCK, N_DOW, N_TREND, n_actions))

    def act(self, state: tuple) -> int:
        """Choose an action using the epsilon-greedy policy."""
        if self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.n_actions))
        return int(np.argmax(self.q[state]))

    def update(self, s, a, r, s_next, done) -> None:
        """Q(s,a) <- Q(s,a) + alpha * [ r + gamma * max_a' Q(s',a') - Q(s,a) ]"""
        future = 0.0 if done else np.max(self.q[s_next])
        target = r + self.gamma * future
        self.q[s][a] += self.alpha * (target - self.q[s][a])

    def save(self, path, actions) -> None:
        table = {}
        for s in np.ndindex(N_STOCK, N_DOW, N_TREND):
            key = f"stock{s[0]}_dow{s[1]}_trend{s[2]}"
            table[key] = [round(float(v), 3) for v in self.q[s]]
        save_json({"actions": actions, "q_table": table}, path)

    def load(self, path) -> None:
        table = load_json(path)["q_table"]
        for s in np.ndindex(N_STOCK, N_DOW, N_TREND):
            self.q[s] = table[f"stock{s[0]}_dow{s[1]}_trend{s[2]}"]

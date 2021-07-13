import numpy as np


class Agent:
    def __init__(self):
        self.actions: list = []

    @staticmethod
    def choose_random_action(actions):
        return np.random.choice(actions)
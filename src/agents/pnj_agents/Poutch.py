from agents.Agent import Agent
from game.actions.ActionList import ActionList


class Poutch(Agent):
    def choose_action(self, state=None, allow_random=True):
        return ActionList.END_TURN

    def create_model(self):
        return

    def initialize(self):
        return

    def store_transition(self, **kwargs):
        return

    def update_memory(self, **kwargs):
        return

    def train_on_memory(self, **kwargs):
        return

    def reset_blocked_actions(self):
        return

    # ======================================================================================================================
    # UTILITY
    def save_model(self):
        return

    def load_model(self):
        return
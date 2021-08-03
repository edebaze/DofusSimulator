from agents.ia.AbstractIA import AbstractIA
from game.actions.ActionList import ActionList


class Poutch(AbstractIA):
    def choose_action(self, **kwargs):
        return ActionList.END_TURN

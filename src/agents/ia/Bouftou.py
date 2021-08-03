from agents.ia.AbstractIA import AbstractIA
from game.actions.ActionList import ActionList


class Bouftou(AbstractIA):
    def choose_action(self, **kwargs):
        return ActionList.END_TURN

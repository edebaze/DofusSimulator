from globals import *
from entity.interface.Map import Map
from entity.Player import Player
from entity.classes import ClassList
import random


class GameController:
    def __init__(self):
        global players

        self.map = Map()

        self.map.create()
        self.create_players()
        self.set_key_bindings()

# ======================================================================================================================
    # INIT METHODS
    @staticmethod
    def create_players():
        global current_player
        global players

        # -- create first player
        rand_box_x = random.randint(0, NUM_BOX_WIDTH-1)
        rand_box_y = random.randint(NUM_BOX_HEIGHT-1 - 5, NUM_BOX_HEIGHT-1)
        x = rand_box_x * BOX_DIM
        y = rand_box_y * BOX_DIM
        player = Player(0, ClassList.IOP)
        player.create((x, y))
        players.append(player)

        # -- create second player
        rand_box_x = random.randint(0, NUM_BOX_WIDTH-1)
        rand_box_y = random.randint(0, 5)
        x = rand_box_x * BOX_DIM
        y = rand_box_y * BOX_DIM
        player = Player(1, ClassList.CRA)
        player.create((x, y))
        players.append(player)

        # -- set first player as current player
        current_player = players[0]
        current_player.activate()

# ======================================================================================================================
    # TURN
    def end_turn(self, event):
        self.next_player()

    def next_player(self):
        global current_player, players

        current_player_index = (current_player.index + 1) % self.num_players
        current_player = players[current_player_index]

        for player in players:
            if player.index == current_player.index:
                player.activate()
            else:
                player.deactivate()

# ======================================================================================================================
    # KEY BINDING
    def set_key_bindings(self):
        root.bind("<space>", self.end_turn)
        return

# ======================================================================================================================
    # DEPENDENT PROPS
    @property
    def num_players(self):
        global players
        return len(players)
from globals import *
import numpy as np
from agents.Agent import Agent
from entity.interface import Map, MapItemList
from entity.Player import Player
from entity.classes import ClassList
from entity.actions.ActionList import ActionList
import random
import copy
import pdb


class GameController:
    MAX_TURN_GAME = 100

    def __init__(self, ia_players: list = [None, None]):
        self.ia_players: list = ia_players
        # self.actions: list = [ActionList.MOVE_LEFT, ActionList.MOVE_RIGHT, ActionList.MOVE_UP, ActionList.MOVE_DOWN, ActionList.CAST_SPELL_1]
        self.actions: list = ActionList.get_actions()
        self.n_actions: int = len(self.actions)

        self.turn: int = 1

# ======================================================================================================================
    # ENV METHODS
    def reset(self):
        self.turn = 1
        self.create_players(self.ia_players)
        return self.get_state()

    def step(self, action):
        continue_playing = CURRENT_PLAYER.do(action)
        if continue_playing:
            continue_playing = CURRENT_PLAYER.continue_playing

        if CURRENT_PLAYER.reward > 500:
            pdb.set_trace()
        (state, reward, done) = (self.get_state(), self.get_reward(), self.get_done())

        if done:
            continue_playing = False

        if not continue_playing:
            self.end_turn()

        return state, reward, done, continue_playing

    def render(self):
        MAP.display(canvas)
        for player in PLAYERS:
            player.render_mode_active = True
            player.display()

        CURRENT_PLAYER.activate()
        self.set_key_bindings()

        root.mainloop()

# ======================================================================================================================
    # ENV SUB_METHODS
    def get_state(self) -> np.ndarray:
        state = copy.copy(MAP.matrix).reshape(MAP.matrix.shape[0] * MAP.matrix.shape[1])
        state = np.concatenate([state, self.get_players_state()])
        return state

    def get_done(self):
        if self.turn >= self.MAX_TURN_GAME:
            return True

        for player in PLAYERS:
            if player.is_dead:
                return True

        return False

    @staticmethod
    def get_players_state():
        state = np.empty(0)
        for player in PLAYERS:
            state = np.concatenate([state, player.get_state()])

        return state

    @staticmethod
    def get_reward() -> int:
        return CURRENT_PLAYER.get_reward()

    @staticmethod
    def create_players(ia_players):
        if len(PLAYERS) > 0:
            globals()['PLAYERS'] = []

        # -- create first player
        box_x = random.randint(1, MAP.BOX_WIDTH - 2)
        box_y = random.randint(MAP.BOX_HEIGHT - 1 - 3, MAP.BOX_HEIGHT - 2)
        player = Player(0, ClassList.IOP, item_value=MapItemList.PLAYER_1, agent=ia_players[0])
        player.name = 'Player 1'
        player.team = 1
        player.create((box_x, box_y))
        PLAYERS.append(player)

        # -- create second player
        box_x = random.randint(1, MAP.BOX_WIDTH - 2)
        box_y = random.randint(1, 4)
        player = Player(1, ClassList.IOP, item_value=MapItemList.PLAYER_2, agent=ia_players[1])
        player.name = 'Player 2'
        player.team = 2
        player.po = 6
        player.create((box_x, box_y))
        PLAYERS.append(player)

        # -- set first player as current player
        globals()['PLAYERS'] = PLAYERS
        globals()['CURRENT_PLAYER'] = PLAYERS[0]
        CURRENT_PLAYER.activate()

# ======================================================================================================================
    # TURN
    def end_turn(self, event=None):
        self.turn += 1
        self.next_player()
        if CURRENT_PLAYER.agent is not None:
            continue_playing = True

            action_counter = 0
            while continue_playing and action_counter < 10:
                action = CURRENT_PLAYER.agent.choose_random_action(self.actions)
                state, reward, done, continue_playing = self.step(action)
                action_counter += 1         # avoid infinite or too long loop

    def next_player(self):
        print(colorama.Fore.RESET, end='')
        current_player_index = (CURRENT_PLAYER.index + 1) % self.num_players
        globals()['CURRENT_PLAYER']  = PLAYERS[current_player_index]

        for player in PLAYERS:
            if player.index == CURRENT_PLAYER.index:
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
        return len(PLAYERS)
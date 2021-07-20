from globals import *
from agents.config.RewardList import RewardList
from game.map import Map, MapItemList
from game.Player import Player
from game.classes import ClassList
from game.actions.ActionList import ActionList

import numpy as np

import copy
import os
import time


class Engine(object):
    MAX_TURN_GAME = 100

    def __init__(self, map_number: int = 0, agents: list = [None, None]):
        self.__name__ = 'Engine'
        self.name                           = self.create_name()
        self.map_number: int                = map_number

        self.map: Map                       = Map(map_number)
        self.players: list                  = []
        self.current_player: Player         = Player()
        self.agents: list                   = agents

        self.actions: list = ActionList.get_actions()
        self.n_actions: int = len(self.actions)

        self.turn: int = 1

# ======================================================================================================================
    def play_game(self):
        self.reset()

        while not self.get_done():
            continue_playing = True
            while continue_playing:
                continue_playing = self.play_action()

            self.end_turn()

        player_1 = self.players[0]
        player_2 = self.players[1]

        return player_1.score, player_2.score, player_1.agent.epsilon, player_2.agent.epsilon

# ======================================================================================================================
    # ENV METHODS
    def reset(self):
        self.turn = 1
        self.create_players()
        self.map.create()
        return self.get_state()

    def step(self, action):
        continue_playing = self.do(action)
        if continue_playing:
            continue_playing = self.current_player.continue_playing

        (state, reward, done) = (self.get_state(), self.get_reward(), self.get_done())

        if done:
            continue_playing = False

        return state, reward, done, continue_playing

# ======================================================================================================================
    # ENV SUB_METHODS
    def get_state(self) -> np.ndarray:
        state = copy.copy(self.map.matrix).reshape(self.map.matrix.shape[0] * self.map.matrix.shape[1])
        state = np.concatenate([state, self.get_players_state()])
        return state

    def get_done(self):
        if self.turn >= self.MAX_TURN_GAME:
            return True

        for player in self.players:
            if player.is_dead:
                return True

        return False

    def get_players_state(self):
        state = np.empty(0)
        for player in self.players:
            state = np.concatenate([state, player.get_state()])

        return state

    def get_reward(self) -> int:
        return self.current_player.get_reward()

    def create_players(self):
        self.players = []

        self.add_player(team=1, class_name=ClassList.IOP)
        self.add_player(team=2, class_name=ClassList.CRA)

        # -- set first player as current player
        self.current_player = self.players[0]
        self.current_player.activate()

    def add_player(self, team, class_name=ClassList.IOP):
        index_player = len(self.players)

        agent = self.agents[index_player]
        model_dir = os.path.join(MODEL_DIR, self.name)
        make_dir(model_dir)

        if agent is not None:
            agent.model_file = os.path.join(model_dir, f'player_{index_player+1}.h5')

        player_name = 'Player ' + str(index_player+1)

        box_x, box_y = self.map.get_initial_player_placement(team)

        # -- create_player
        player = Player(index_player, class_name=class_name, agent=agent)
        player.name = player_name
        player.team = team
        player.box_x = box_x
        player.box_y = box_y
        self.map.place_player(player)
        self.players.append(player)

    def evaluate_next_rewards(self):
        q_table = np.zeros(len(self.actions))
        for i in range(len(self.actions)):
            env = self.duplicate()
            action = self.actions[i]

            new_state, reward, done, continue_playing = env.step(action)

            q_table[i] = reward

        return q_table

# ======================================================================================================================
    # TURN
    def end_turn(self):
        self.turn += 1
        self.next_player()

    def next_player(self):
        print(colorama.Fore.RESET, end='')
        current_player_index = (self.current_player.index + 1) % self.num_players
        self.current_player = self.players[current_player_index]

        for player in self.players:
            if player.index == self.current_player.index:
                player.activate()
            else:
                player.deactivate()

    def play_action(self, action=None):
        agent = self.current_player.agent
        state = self.get_state()  # -- get initial state of the turn

        if action is None:
            action = agent.choose_action(state)

        new_state, reward, done, continue_playing = self.step(action)
        agent.store_transition(
            state=state,
            action=action,
            reward=reward,
            new_state=new_state,
            done=done
        )

        # TODO : remove
        agent.learn()

        if done:
            continue_playing = False

        return continue_playing

# ======================================================================================================================
    # DEPENDENT PROPS
    @property
    def num_players(self):
        return len(self.players)


# ======================================================================================================================
    # PLAYER ACTIONS
# ======================================================================================================================
    # MOVE
    def move_to_position(self, player, box_x, box_y):

        move_box_x = box_x - player.box_x
        move_box_y = box_y - player.box_y
        required_pm = abs(move_box_x) + abs(move_box_y)
        if not self.is_move_ok(player, box_x, box_y):
            player.reward += RewardList.BAD_MOVEMENT
            return

        player.box_x = box_x
        player.box_y = box_y
        self.move(player, required_pm)

    # __________________________________________________________________________________________________________________
    def is_move_ok(self, player, box_x, box_y, required_pm=1):
        if box_x >= self.map.BOX_WIDTH or box_y >= self.map.BOX_HEIGHT:
            player.print('OUTSIDE THE MAP')
            return False

        if player.pm < required_pm:
            player.print('NO PM LEFT')
            return False

        if not self.map.is_empty(box_x, box_y):
            player.print('BOX NOT EMPTY')
            return False

        return True

    # __________________________________________________________________________________________________________________
    def move(self, player, pm_used: int = 1):
        player.pm -= pm_used
        self.map.place_player(player)

    # __________________________________________________________________________________________________________________
    def move_left(self, player):
        box_x = player.box_x - 1
        if not self.is_move_ok(player, box_x, player.box_y):
            player.reward += RewardList.BAD_MOVEMENT
            return

        player.box_x = box_x
        self.move(player)

    # __________________________________________________________________________________________________________________
    def move_right(self, player):
        box_x = player.box_x + 1
        if not self.is_move_ok(player, box_x, player.box_y):
            player.reward += RewardList.BAD_MOVEMENT
            return

        player.box_x = box_x
        self.move(player)

    # __________________________________________________________________________________________________________________
    def move_up(self, player):
        box_y = player.box_y - 1
        if not self.is_move_ok(player, player.box_x, box_y):
            player.reward += RewardList.BAD_MOVEMENT
            return

        player.box_y = box_y
        self.move(player)

    # __________________________________________________________________________________________________________________
    def move_down(self, player):
        box_y = player.box_y + 1
        if not self.is_move_ok(player, player.box_x, box_y):
            player.reward += RewardList.BAD_MOVEMENT
            return

        player.box_y = box_y
        self.move(player)

# ======================================================================================================================
    # SPELLS
    def auto_cast_spell(self, spell_index):
        """ select a spell and cast it. If player is in range attack him otherwise cast in the void """

        player = self.current_player

        spell = player.class_.spells[spell_index]
        player.select_spell(spell.type)
        if player.selected_spell is None:
            return

        po = spell.po + int(spell.is_po_mutable) * player.po

        # =================================================================================
        # CHECK IF PLAYER IS IN RANGE
        for target_player in self.players:
            if target_player.item_value == player.item_value:
                continue
            distance_box_x = abs(target_player.box_x - player.box_x)
            distance_box_y = abs(target_player.box_y - player.box_y)
            distance_box = distance_box_x + distance_box_y

            if distance_box <= po:
                player.hit(target_player)
            else:
                player.reward += RewardList.BAD_SPELL_CASTING
                player.print(f'{spell.name} CASTED ON NOTHING')

        player.pa -= player.selected_spell.pa   # use PA
        player.deselect_spell()

    # __________________________________________________________________________________________________________________
    def cast_spell(self, box_x, box_y):
        """ cast the selected spell """

        player = self.current_player

        if player.selected_spell is None:
            player.print('NO SPELL SELECTED')
            return

        spell = player.selected_spell

        # =================================================================================
        # CHECK IS IN MAP
        if not (self.map.BOX_WIDTH > box_x >= 0 and self.map.BOX_HEIGHT > box_y >= 0):
            player.print('OUTSIDE THE MAP')
            player.deselect_spell()
            return

        # =================================================================================
        # CHECK IS IN PO
        po = spell.po + int(spell.is_po_mutable) * player.po
        num_box = abs(player.box_x - box_x) + abs(player.box_y - box_y)
        if num_box > po:
            player.print('SPELL OUT OF PO RANGE')
            player.deselect_spell()
            return

        box_content = self.map.box(box_x, box_y)

        # =================================================================================
        # CHECK OTHER PLAYERS
        if box_content > MapItemList.PLAYER_1:
            for targeted_player in self.players:
                if targeted_player.item_value == box_content:
                    player.hit(targeted_player)

        # =================================================================================
        # CHECK VOID
        elif box_content == MapItemList.VOID:
            player.print('HIT VOID')
            player.deselect_spell()
            return

        # =================================================================================
        # CHECK BLOCK
        elif box_content == MapItemList.BLOCK:
            player.print('HIT BLOCK')
            player.deselect_spell()
            return

        # =================================================================================
        # CHECK EMPTY
        elif box_content == MapItemList.EMPTY:
            player.print('HIT EMPTY CASE')

        player.pa -= spell.pa  # use PA
        player.deselect_spell()

# ======================================================================================================================
    # UTILITY
    def duplicate(self):
        """
            Duplicate Engine to evaluate next rewards
        :return:
        """
        copy_engine = copy.copy(self)
        copy_engine.map = copy.copy(self.map)
        copy_engine.map.matrix = copy.copy(self.map.matrix)
        copy_engine.current_player = copy.copy(self.current_player)
        copy_engine.current_player.print_mode_active = False

        copy_engine.players = []
        for i in range(len(self.players)):
            copy_player = self.players[i].duplicate()
            copy_player.print_mode_active = False
            copy_engine.players.append(copy_player)

        return copy_engine

    @staticmethod
    def create_name() -> str:
        """ create name from current timestamp """
        date = time.time_ns()
        return str(date)

# ======================================================================================================================
    # UTILITY
    def get_info(self):
        return {
            'turn': self.turn,
            'actions': '/'.join(self.actions)
        }

# ======================================================================================================================
    def do(self, action: int) -> bool:
        """
            execute action from ActionList
        :param action:
        :return: bool -> continue playing or not
        """
        player = self.current_player

        player.last_action = action
        player.num_actions_in_turn += 1  # increase number of actions taken in the turn (by the agent)

        if action == ActionList.END_TURN:
            player.print('END_TURN')
            return False

        elif action == ActionList.MOVE_LEFT:
            player.print('MOVE_LEFT')
            self.move_left(self.current_player)

        elif action == ActionList.MOVE_RIGHT:
            player.print('MOVE_RIGHT')
            self.move_right(self.current_player)

        elif action == ActionList.MOVE_UP:
            player.print('MOVE_UP')
            self.move_up(self.current_player)

        elif action == ActionList.MOVE_DOWN:
            player.print('MOVE_DOWN')
            self.move_down(self.current_player)

        elif action == ActionList.CAST_SPELL_1:
            self.auto_cast_spell(1)

        elif action == ActionList.CAST_SPELL_2:
            self.auto_cast_spell(2)

        elif action == ActionList.CAST_SPELL_3:
            self.auto_cast_spell(3)

        else:
            print(f'Unkown action {action}')

        return True
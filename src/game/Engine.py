from globals import *

from game.spells import Spell, SpellDirectionList
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
    MAX_TURN_GAME = 50

    def __init__(self, map_number: int = 0, agents: list = [None, None], flag_create_dir: bool = True):
        self.__name__ = 'Engine'
        self.name                           = self.create_name()
        self.map_number: int                = map_number

        self.map: Map                       = Map(map_number)
        self.players: list                  = []
        self.current_player: Player         = Player()
        self.agents: list                   = agents

        self.actions: list                  = ActionList.get_actions()
        self.n_actions: int                 = len(self.actions)

        self.turn: int                      = 1

        self.model_dir: str                 = os.path.join(MODEL_DIR, self.name)

        if flag_create_dir:
            make_dir(self.model_dir)

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

        return player_1.score, player_2.score

# ======================================================================================================================
    # ENV METHODS
    def reset(self):
        self.turn = 1
        self.map.create()
        self.create_players()
        return self.get_state()

    def step(self, action):
        continue_playing = self.do(action)
        if continue_playing:
            continue_playing = self.current_player.continue_playing

        (state, reward, done) = (self.get_state(), self.get_reward(), self.get_done())

        # if game over
        if done:
            # -- stop continue playing
            continue_playing = False
            
            # -- if game has stopped because the max turn was reached
            if self.turn >= self.MAX_TURN_GAME:
                # -- add max turn reward to the current reward and all players total score
                reward += RewardList.REACH_MAX_TURN
                for player in self.players:
                    player.score += RewardList.REACH_MAX_TURN

        return state, reward, done, continue_playing

# ======================================================================================================================
    # ENV SUB_METHODS
    def get_state(self) -> np.ndarray:
        return np.asarray([self.map.matrix, self.get_players_state()])

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
        self.map.create_player_mask_pm(self.current_player)

    def add_player(self, team, class_name=ClassList.IOP):
        index_player = len(self.players)

        agent = self.agents[index_player]

        if agent is not None:
            agent.model_filename = os.path.join(self.model_dir, f'player_{index_player+1}.h5')

        player_name = 'Player ' + str(index_player+1)

        box_x, box_y = self.map.get_initial_player_placement(team)

        # -- create_player
        player = Player(index_player, class_name=class_name, agent=agent)
        if class_name == ClassList.IOP:
            player.pm += 1
            player.hp += 50
        player.name = player_name
        player.team = team
        player.box_x = box_x
        player.box_y = box_y
        self.map.place_player(player, flag_set_mask_pm=False)
        self.players.append(player)

# ======================================================================================================================
    # TURN
    def end_turn(self):
        if self.get_done():
            return
        self.turn += 1
        self.next_player()

    def next_player(self):
        print(colorama.Fore.RESET, end='')
        current_player_index = (self.current_player.index + 1) % self.num_players

        # -- deactivate current player
        self.current_player.deactivate()
        self.map.remove_player_mask_pm()    # remove current mask pm

        # -- activate new current player
        self.current_player = self.players[current_player_index]
        self.current_player.activate()
        self.map.create_player_mask_pm(self.current_player)

    def play_action(self, action=None):
        agent = self.current_player.agent
        state = self.get_state()  # -- get initial state of the turn

        if action is None:
            action = agent.choose_action(state)

        new_state, reward, done, continue_playing = self.step(action)
        
        action_table = np.zeros(self.n_actions).astype(np.bool) 
        action_table[action] = True
        agent.store_transition(
            state=state,
            action_table=action_table,
            reward=reward,
            new_state=new_state,
            done=done
        )

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
    def select_spell(self, spell: Spell):
        player = self.current_player
        player.select_spell(spell)
        self.map.create_spell_mask(player)

    # __________________________________________________________________________________________________________________
    def deselect_spell(self):
        self.current_player.deselect_spell()
        self.map.remove_mask(MapItemList.MASK_SPELL)

    # __________________________________________________________________________________________________________________
    def auto_cast_spell(self, spell_index):
        """ select a spell and cast it. If player is in range attack him otherwise cast in the void """

        player = self.current_player

        spell = player.class_.spells[spell_index]
        self.select_spell(spell)
        if player.selected_spell is None:
            return

        target_player = None
        for target_player in self.players:
            if target_player.team != self.current_player.team:
                break

        if target_player is None:
            print('Error : no player to target')
            return

        self.cast_spell(target_player.box_x, target_player.box_y)

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
        box_content = self.map.box_content(box_x, box_y)
        if box_content is None:
            player.print('OUTSIDE THE MAP')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK IS IN PO
        index_spell_mask = self.map.item_values.index(MapItemList.MASK_SPELL)
        if box_content[index_spell_mask] == 0:
            player.print('SPELL OUT OF PO RANGE')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK EMPTY
        elif box_content[self.map.item_empty_index] == 1:
            player.print('HIT EMPTY CASE')

        # =================================================================================
        # CHECK VOID
        elif box_content[self.map.item_void_index] == 1:
            player.print('HIT VOID')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK BLOCK
        elif box_content[self.map.item_block_index] == 1:
            player.print('HIT BLOCK')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK OTHER PLAYERS
        for index_player in range(len(MapItemList.PLAYERS)):
            item_value = MapItemList.PLAYERS[index_player]          # get player item_value
            item_index = self.map.item_values.index(item_value)     # get index value of player
            # -- if player is in box_content
            if box_content[item_index] == 1:
                targeted_player = self.players[index_player]
                self.hit(targeted_player, self.current_player.selected_spell)

        player.pa -= spell.pa  # use PA
        self.deselect_spell()

    def hit(self, player: Player, spell: Spell):
        """
            current player is hitting an other player with current selected spell
        :param player:
        :return:
        """
        # -- if targeted player is already dead, nothing to do
        if player.is_dead:
            return

        self.current_player.print(f'{spell.name}: ', end='')

        # -- set true damages
        damages = player.get_hit(spell.damages(), spell.elem)
        # -- add bump damages
        bumb_x, bumb_y = SpellDirectionList.get_direction_x_y(player.box_x, player.box_y, self.current_player.box_x, self.current_player.box_y)
        for i in range(spell.bump):
            if not self.map.is_empty(player.box_x + bumb_x, player.box_y + bumb_y):
                bumb_damages = (spell.bump - i) * 10
                damages += player.get_hit(bumb_damages, Spell.ELEMENT_BUMP)
                break
            player.box_x += bumb_x
            player.box_y += bumb_y
            self.map.place_player(player, flag_set_mask_pm=False)

        self.current_player.print(f'{damages} hp')

        # update reward if player is not an ally
        if player.team != self.current_player.team:
            self.current_player.reward += damages * RewardList.DAMAGES
        else:
            self.current_player.reward -= damages * RewardList.DAMAGES  # negative reward for friendly fire

        # -- if targeted player is dead
        if player.is_dead:
            if player.team != self.current_player.team:
                self.current_player.reward += RewardList.KILL  # positive reward if not ally
            else:
                self.current_player.reward -= RewardList.KILL  # negative reward if ally

        return damages

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
        self.deselect_spell()               # deselect current spell if any

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

        elif action == ActionList.CAST_SPELL_4:
            self.auto_cast_spell(4)

        else:
            print(f'Unkown action {action}')

        return True
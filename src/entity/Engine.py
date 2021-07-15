from globals import *
import numpy as np
from agents.Agent import Agent
from agents.config.RewardList import RewardList
from entity.GUI import GUI
from entity.interface import Map, MapItemList
from entity.Player import Player
from entity.classes import ClassList
from entity.actions.ActionList import ActionList
import random
import copy
import time
import pdb


class Engine:
    MAX_TURN_GAME = 100

    def __init__(self, agents: list = [None, None]):
        self.gui: GUI                       = GUI()
        self.map: Map                       = Map()
        self.players: list                  = []
        self.current_player: Player
        self.agents: list                   = agents

        self.actions: list = ActionList.get_actions()
        self.n_actions: int = len(self.actions)

        # TODO : check that
        self.sleep_mode_active = False
        self.render_mode_active = False

        self.turn: int = 1

# ======================================================================================================================
    # ENV METHODS
    def reset(self):
        self.turn = 1
        self.create_players()
        return self.get_state()

    def step(self, action):
        continue_playing = self.do(action)
        if continue_playing:
            continue_playing = self.current_player.continue_playing

        (state, reward, done) = (self.get_state(), self.get_reward(), self.get_done())

        if done:
            continue_playing = False

        if not continue_playing:
            self.end_turn()

        return state, reward, done, continue_playing

    def render(self):
        self.map.display(canvas)
        for player in self.players:
            player.render_mode_active = True
            player.sleep_mode_active = True
            player.display()

        self.current_player.activate()
        
        # TODO : remove
        self.set_key_bindings()

        root.mainloop()

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

        # -- create first player
        box_x = random.randint(1, self.map.BOX_WIDTH - 2)
        box_y = random.randint(self.map.BOX_HEIGHT - 1 - 3, self.map.BOX_HEIGHT - 2)
        player = Player(0, ClassList.IOP, item_value=MapItemList.PLAYER_1, agent=self.agents[0])
        player.name = 'Player 1'
        player.team = 1
        player.box_x = box_x
        player.box_y = box_y
        self.place_player_on_map(player)
        self.players.append(player)

        # -- create second player
        box_x = random.randint(1, self.map.BOX_WIDTH - 2)
        box_y = random.randint(1, 4)
        player = Player(1, ClassList.CRA, item_value=MapItemList.PLAYER_2, agent=self.agents[1])
        player.name = 'Player 2'
        player.team = 2
        player.po = 6
        player.box_x = box_x
        player.box_y = box_y
        self.place_player_on_map(player)
        self.players.append(player)

        # -- set first player as current player
        self.current_player = self.players[0]
        self.current_player.activate()

# ======================================================================================================================
    # TURN
    def end_turn(self, event=None):
        self.turn += 1
        self.next_player()

        # -- AGENT
        if self.current_player.agent is not None:
            self.agent_turn(self.current_player.agent)

    def next_player(self):
        print(colorama.Fore.RESET, end='')
        current_player_index = (self.current_player.index + 1) % self.num_players
        self.current_player = self.players[current_player_index]

        for player in self.players:
            if player.index == self.current_player.index:
                player.activate()
            else:
                player.deactivate()

    def agent_turn(self, agent):
        continue_playing = True
        done = False
        state = self.get_state()        # -- get initial state of the turn

        while continue_playing and not done:
            action = agent.choose_action(state)
            new_state, reward, done, continue_playing = self.step(action)

            agent.store_transition(
                state=state,
                action=action,
                reward=reward,
                new_state=new_state,
                done=done
            )

            agent.learn()
            state = new_state

        self.end_turn()

# ======================================================================================================================
    # KEY BINDING
    def set_key_bindings(self):
        root.bind("<space>", self.end_turn)
        return

# ======================================================================================================================
    # UTILITY
    def sleep(self, t=SLEEP_TIME):
        if self.sleep_mode_active:
            time.sleep(t)

# ======================================================================================================================
    # DEPENDENT PROPS
    @property
    def num_players(self):
        return len(self.players)

# ======================================================================================================================
    # MAP
    def place_player_on_map(self, player):
        # -- get previous position of the item
        pos = np.argwhere(self.map.matrix == player.item_value)
        if len(pos) != 0:
            # -- delete the item
            pos = pos[0]
            self.map.matrix[pos[0], pos[1]] = MapItemList.EMPTY

        # -- place the item
        self.map.place(player.box_x, player.box_y, player.item_value)

# ======================================================================================================================
    # PLAYER ACTIONS
# ======================================================================================================================
    def do(self, action: int) -> bool:
        """
            execute action from ActionList
        :param action:
        :return: bool -> continue playing or not
        """
        player = self.current_player

        player.num_actions_in_turn += 1  # increase number of actions taken in the turn (by the agent)
        self.sleep(0.5)  # sleep to be able to see the actions

        if action == ActionList.END_TURN:
            player.print('END_TURN')
            # return False
            return True  # TODO : set back to FALSE

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
            self.print(f'Unkown action {action}')

        root.update()

        return True

# ======================================================================================================================
    # MOVE

    # __________________________________________________________________________________________________________________
    def is_move_ok(self, player, box_x, box_y):
        if player.pm == 0:
            player.print('NO PM LEFT')
            return False

        if not self.map.is_empty(box_x, box_y):
            player.print('BOX NOT EMPTY')
            return False

        return True

    # __________________________________________________________________________________________________________________
    def move(self, player, pm_used: int = 1):
        player.pm -= pm_used
        self.place_player_on_map(player)

        # TODO : TO GUI
        if self.render_mode_active:
            INFO_BAR.set_pm(self.pm)
            self.label.place(x=self.box_x * MAP.BOX_DIM, y=self.box_y * MAP.BOX_DIM)

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

        # TODO : GUI
        if self.render_mode_active:
            INFO_BAR.set_pa(self.pa)  # display use of PA in the info bar

    # __________________________________________________________________________________________________________________
    def cast_spell(self, event=None):
        """ cast the selected spell """

        player = self.current_player

        if player.selected_spell is None:
            player.print('NO SPELL SELECTED')
            return

        spell = player.selected_spell
        box_x_selected, box_y_selected = self.map.get_selected_box(event)

        # =================================================================================
        # CHECK IS IN MAP
        if not (self.map.BOX_WIDTH > box_x_selected >= 0 and self.map.BOX_HEIGHT > box_y_selected >= 0):
            player.print('OUTSIDE THE MAP')
            player.deselect_spell()
            return

        # =================================================================================
        # CHECK IS IN PO
        po = spell.po + int(spell.is_po_mutable) * player.po
        num_box = abs(player.box_x - box_x_selected) + abs(player.box_y - box_y_selected)
        if num_box > po:
            player.print('SPELL OUT OF PO RANGE')
            player.deselect_spell()
            return

        box_content = self.map.box(box_x_selected, box_y_selected)

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

        # TODO : GUI
        if self.render_mode_active:
            INFO_BAR.set_pa(player.pa)  # display use of PA in the info bar
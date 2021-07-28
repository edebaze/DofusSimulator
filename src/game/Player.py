from tkinter import Label
from globals import *
from agents import Agent, RewardList
from game.map.MapItemList import MapItemList
from game.map.Map import Map
from game.actions.ActionList import ActionList
from game.classes import ClassList, Class
from game.spells import SpellList, Spell

import numpy as np
import copy


class Player:
    MAX_ACTIONS_IN_TURN = 10

    MAX_HP = 150
    MAX_PA = 12
    MAX_PM = 6
    MAX_PO = 6

    def __init__(self, index: int = 0, class_name: str = '', agent: (None, Agent) = None):
        # Identity
        self.agent = agent
        self.class_: Class = ClassList.get(class_name) if class_name != '' else None
        self.index: int = index
        self.team: int = 0
        self.name: str = ''

        # MAP position
        self.box_x: int = 0
        self.box_y: int = 0
        self.item_value = MapItemList.get_player_value(index)

        # Canvas items
        self.tk_img = None                      # image of the player (PhotoImage object)
        self.label: Label = None                # label of the image in Canvas

        # Statistics
        self.is_dead: bool = False
        self.BASE_HP = 100          # initial HP of the player
        self.BASE_PA = 7            # initial PA of the player
        self.BASE_PM = 3            # initial PM of the player
        self.BASE_PO = 2            # initial PO of the player
        self.hp = self.BASE_HP      # current HP of the player
        self.pa = self.BASE_PA      # current PA of the player
        self.pm = self.BASE_PM      # current PM of the player
        self.po = self.BASE_PO      # current PO of the player

        # Agent state
        self.last_action: int = ActionList.END_TURN     # last action taken this turn
        self.is_current_player: bool = False            # is currently playing

        # Agent Data
        self.score: int = 0
        self.reward: int = 0                # reward of the last action
        self.num_actions_in_turn: int = 0   # number of actions taken during the turn

        # Rendering
        self.print_mode_active: bool = False

        self.selected_spell: Spell = None       # current selected spell

# ======================================================================================================================
    # INITIALIZATION
    def activate(self):
        """
            activate player when his turn begins
        """
        self.last_action = ActionList.END_TURN  # reset last action taken this turn
        self.is_current_player = True           # set as current player this turn
        self.agent.blocked_actions = []         # reset blocked actions
        return

    def deactivate(self):
        """
            deactivate player when his turn ends
        """
        if self.is_current_player:
            self.reward += RewardList.ROUND_START   # remove reward at the end of a round
            self.is_current_player = False          # remove as current player

        self.new_turn()
        self.deselect_spell()

    def new_turn(self):
        self.pa = self.BASE_PA
        self.pm = self.BASE_PM
        self.num_actions_in_turn = 0

# ======================================================================================================================
    # ENV METHODS
    def get_reward(self):
        """
            return reward and reset it
        :return:
        """
        reward = self.reward
        self.score += reward
        self.reward = 0
        return reward

# ======================================================================================================================
    # ACTIONS
    def select_spell(self, spell: Spell):
        self.deselect_spell()

        if self.pa - spell.pa < 0:
            self.print(f"CAN'T SELECT SPELL {spell.name}")
            self.reward += RewardList.BAD_SPELL_SELECTION
            return

        self.selected_spell = spell

    # __________________________________________________________________________________________________________________
    def deselect_spell(self):
        if self.selected_spell is not None:
            self.selected_spell = None

    # __________________________________________________________________________________________________________________
    def get_hit(self, damages: int, elem: str = ''):
        """
            get hit with a spell
        :param damages: number of damage to inflict
        :param elem: elem of damages
        :return:
        """

        prev_hp = self.hp                       # keep track of current hp for the true_damages calculation
        self.hp = max(0, self.hp - damages)     # set player hp (min = 0)

        # -- reward calculation
        true_damages = prev_hp - self.hp
        self.reward += true_damages * RewardList.HP_LOSS    # increment reward with true damages

        if self.hp <= 0 and not self.is_dead:
            self.die()

        return true_damages

    # __________________________________________________________________________________________________________________
    def die(self):
        self.is_dead = True
        self.reward += RewardList.DIE

# ======================================================================================================================
    # UTILITY
    def print(self, msg, end='\n'):
        if not self.print_mode_active:
            return
        color = colorama.Fore.RED if self.team == 1 else colorama.Fore.BLUE
        print(f'{color}{msg}{colorama.Fore.RESET}', end=end)

    def duplicate(self):
        copy_player = copy.copy(self)
        copy_player.tk_img = ''
        copy_player.label = ''
        return copy_player


# ======================================================================================================================
    # DEPENDENT PROPS
    @property
    def x(self) -> int:
        return self.box_x * Map.BOX_DIM

    # __________________________________________________________________________________________________________________
    @property
    def y(self) -> int:
        return self.box_y * Map.BOX_DIM

    # __________________________________________________________________________________________________________________
    @property
    def continue_playing(self) -> bool:
        if self.num_actions_in_turn >= self.MAX_ACTIONS_IN_TURN:
            return False

        spells_pa = []
        for spell in self.class_.spells:
            if spell.pa > 0:
               spells_pa.append(spell.pa)

        min_pa_action = min(spells_pa)
        if self.pm == 0 and self.pa < min_pa_action:
            return False

        return True

# ======================================================================================================================
    # ENV ACTIONS
    def get_state(self):
        return np.asarray([
            self.pa / self.MAX_PA,
            self.pm / self.MAX_PM,
            self.hp / self.MAX_HP,
            self.po / self.MAX_PO,
            self.pa / self.BASE_PA,
            self.pm / self.BASE_PM,
            self.hp / self.BASE_HP,
            self.po / self.BASE_PO,
            self.box_x / Map.MAX_SIZE,
            self.box_y / Map.MAX_SIZE,
            int(self.is_current_player),
            self.last_action / len(ActionList.get_actions()),
        ])
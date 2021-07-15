from globals import *
from agents import Agent, RewardList
from entity.interface.MapItemList import MapItemList
from entity.actions.ActionList import ActionList
from entity.classes import ClassList, Class
from entity.spells import SpellList, Spell
from PIL import Image, ImageTk
import time
import numpy as np


class Player:
    MAX_ACTIONS_IN_TURN = 10

    def __init__(self, index: int, class_name: str, item_value: int, agent: (None, Agent) = None):
        # Identity
        self.agent = agent
        self.class_: Class = ClassList.get(class_name)
        self.index: int = index
        self.team: int = 0
        self.name: str = ''

        # MAP position
        self.box_x: int = 0
        self.box_y: int = 0
        self.item_value = item_value

        # Canvas items
        self.tk_img = None                      # image of the player (PhotoImage object)
        self.label: (None, Label) = None        # label of the image in Canvas
        self.mask_pm: list = []                 # mask for pm (constraining all ids of rect)
        self.mask_po: list = []                 # mask for po (constraining all ids of rect)

        # Stats
        self.BASE_HP = 100          # initial HP of the player
        self.BASE_PA = 7            # initial PA of the player
        self.BASE_PM = 3            # initial PM of the player
        self.BASE_PO = 2            # initial PO of the player
        self.hp = self.BASE_HP      # current HP of the player
        self.pa = self.BASE_PA      # current PA of the player
        self.pm = self.BASE_PM      # current PM of the player
        self.po = self.BASE_PO      # current PO of the player

        # Agent Data
        self.reward: int = 0                # reward of the last action
        self.num_actions_in_turn: int = 0   # number of actions taken during the turn

        # Other
        self.render_mode_active: bool = False
        self.print_mode_active: bool = True
        self.is_dead: bool = False

        self.selected_spell: (None, Spell) = None       # current selected spell

# ======================================================================================================================
    # INITIALIZATION
    def create(self, pos: tuple):
        (self.box_x, self.box_y) = pos
        self.place()

    def display(self):
        self.tk_img = ImageTk.PhotoImage(Image.open(self.class_.img_path).resize((MAP.BOX_DIM, MAP.BOX_DIM)))
        self.label = Label(canvas, image=self.tk_img)
        self.label.place(x=self.x, y=self.y, anchor=NW)

    def round_starts(self):
        self.reset()

    def activate(self):
        """
            activate player bindings when his round starts
        """
        self.round_starts()

        if self.render_mode_active:
            self.add_info()                 # display player info to the info_bar
            self.set_click_key_bindings()   # set key bindings
            self.bind_movements()           # bind movement keys
            self.set_hover()                # create hover bindings

    def deactivate(self):
        """
            deactivate player when his turn ends
        """
        self.round_starts()
        self.deselect_spell()

        if self.render_mode_active:
            self.label.unbind("<Enter>")
            self.label.unbind("<Leave>")

    def reset(self):
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
        self.reward = 0
        return reward

# ======================================================================================================================
    # CLICK BINDINGS
    def set_click_key_bindings(self):
        canvas.bind("<Button-1>", self.move_to_position)
        root.bind("<Button-3>", self.get_box_content)
        return

    def reset_left_click_binding(self, event=None):
        self.deselect_spell()
        canvas.bind("<Button-1>", self.move_to_position)

    @staticmethod
    def get_box_content(event):
        x, y = MAP.get_selected_box(event)
        content = MAP.box(x, y)
        print(f'(x={x}, y={y}) : {content}')

# ======================================================================================================================
    # HOVER BINDINGS
    def set_hover(self):
        self.label.bind('<Enter>', self.create_mask_pm)
        self.label.bind('<Leave>', self.delete_mask_pm)
        return

# ======================================================================================================================
    # MOVEMENT
    def bind_movements(self):
        """
            bind movement keys
        :return:
        """
        root.bind('<Left>', self.move_left)
        root.bind('<Right>', self.move_right)
        root.bind('<Up>', self.move_up)
        root.bind('<Down>', self.move_down)

    # __________________________________________________________________________________________________________________
    def move_to_position(self, event):
        """
            move player to selected position
        :param event:
        :return:
        """

        box_x_selected, box_y_selected = MAP.get_selected_box(event)
        if not MAP.is_empty(box_x_selected, box_y_selected):
            self.print('BOX NOT EMPTY')
            return

        move_box_x = box_x_selected - self.box_x
        move_box_y = box_y_selected - self.box_y
        pm_used = abs(move_box_x) + abs(move_box_y)

        self.print(f'{move_box_x}, {move_box_y}')

        if pm_used > self.pm:
            self.print('NOT ENOUGH PM')
            return

        self.box_x = box_x_selected
        self.box_y = box_y_selected
        self.move(pm_used)

    # __________________________________________________________________________________________________________________
    def move(self, pm_used=1):
        self.pm -= pm_used
        self.place()

        if self.render_mode_active:
            INFO_BAR.set_pm(self.pm)
            self.label.place(x=self.box_x * MAP.BOX_DIM, y=self.box_y * MAP.BOX_DIM)

    # __________________________________________________________________________________________________________________
    def is_move_ok(self, box_x, box_y):
        if self.pm == 0:
            self.print('NO PM LEFT')
            return False

        if not MAP.is_empty(box_x, box_y):
            self.print('BOX NOT EMPTY')
            return False

        return True

    # __________________________________________________________________________________________________________________
    def move_left(self, event=None):
        box_x = self.box_x - 1

        if not self.is_move_ok(box_x, self.box_y):
            self.reward += RewardList.BAD_MOVEMENT
            return

        self.box_x = box_x
        self.move()

    # __________________________________________________________________________________________________________________
    def move_right(self, event=None):
        box_x = self.box_x + 1

        if not self.is_move_ok(box_x, self.box_y):
            self.reward += RewardList.BAD_MOVEMENT
            return

        self.box_x = box_x
        self.move()

    # __________________________________________________________________________________________________________________
    def move_up(self, event=None):
        box_y = self.box_y - 1

        if not self.is_move_ok(self.box_x, box_y):
            self.reward += RewardList.BAD_MOVEMENT
            return

        self.box_y = box_y
        self.move()

    # __________________________________________________________________________________________________________________
    def move_down(self, event=None):
        box_y = self.box_y + 1

        if not self.is_move_ok(self.box_x, box_y):
            self.reward += RewardList.BAD_MOVEMENT
            return

        self.box_y = box_y
        self.move()

# ======================================================================================================================
    # ACTIONS
    def auto_cast_spell(self, spell_index):
        """ select a spell and cast it. If player is in range attack him otherwise cast in the void """
        spell = self.class_.spells[spell_index]
        self.select_spell(spell.type)
        if self.selected_spell is None:
            return

        po = spell.po + int(spell.is_po_mutable) * self.po

        # =================================================================================
        # CHECK IF PLAYER IS IN RANGE
        for player in PLAYERS:
            if player.item_value == self.item_value:
                continue
            distance_box_x = abs(player.box_x - self.box_x)
            distance_box_y = abs(player.box_y - self.box_y)
            distance_box = distance_box_x + distance_box_y

            if distance_box <= po:
                self.hit(player)
            else:
                self.reward += RewardList.BAD_SPELL_CASTING
                self.print(f'{spell.name} CASTED ON NOTHING')

        self.pa -= self.selected_spell.pa   # use PA
        self.deselect_spell()

        if self.render_mode_active:
            INFO_BAR.set_pa(self.pa)  # display use of PA in the info bar

    # __________________________________________________________________________________________________________________
    def select_spell(self, spell_type: int):
        self.deselect_spell()

        spell = SpellList.get(spell_type)
        if self.pa - spell.pa < 0:
            self.print(f"CAN'T SELECT SPELL {spell.name}")
            self.reward += RewardList.BAD_SPELL_SELECTION
            return

        self.selected_spell = spell

        if self.render_mode_active:
            canvas.unbind("<Button-1>")
            root.bind("<Button-1>", self.cast_spell)
            po = spell.po + int(spell.is_po_mutable) * self.po
            self.create_mask_po(po)

    # __________________________________________________________________________________________________________________
    def deselect_spell(self):
        if self.selected_spell is not None:
            self.selected_spell = None

            if self.render_mode_active:
                self.reset_left_click_binding()
                self.delete_mask_po()
                root.unbind('<Button-1>')

    # __________________________________________________________________________________________________________________
    def cast_spell(self, event):
        """ cast the selected spell """
        if self.selected_spell is None:
            self.print('NO SPELL SELECTED')
            return

        spell = self.selected_spell
        box_x_selected, box_y_selected = MAP.get_selected_box(event)

        # =================================================================================
        # CHECK IS IN MAP
        if not (MAP.BOX_WIDTH > box_x_selected >= 0 and MAP.BOX_HEIGHT > box_y_selected >= 0):
            self.print('OUTSIDE THE MAP')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK IS IN PO
        po = spell.po + int(spell.is_po_mutable) * self.po
        num_box = abs(self.box_x - box_x_selected) + abs(self.box_y - box_y_selected)
        if num_box > po:
            self.print('SPELL OUT OF PO RANGE')
            self.deselect_spell()
            return

        box_content = MAP.box(box_x_selected, box_y_selected)

        # =================================================================================
        # CHECK OTHER PLAYERS
        if box_content > MapItemList.PLAYER_1:
            for player in PLAYERS:
                if player.item_value == box_content:
                    self.hit(player)

        # =================================================================================
        # CHECK VOID
        elif box_content == MapItemList.VOID:
            self.print('HIT VOID')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK BLOCK
        elif box_content == MapItemList.BLOCK:
            self.print('HIT BLOCK')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK EMPTY
        elif box_content == MapItemList.EMPTY:
            self.print('HIT EMPTY CASE')

        self.pa -= self.selected_spell.pa   # use PA
        self.deselect_spell()

        if self.render_mode_active:
            INFO_BAR.set_pa(self.pa)  # display use of PA in the info bar

    # __________________________________________________________________________________________________________________
    def hit(self, player):
        """
            current player is hitting an other player with current selected spell
        :param player:
        :return:
        """
        damages = self.selected_spell.damages()
        self.print(f'{self.selected_spell.name}: {damages} hp')
        player.get_hit(damages)

        # update reward if player is not an ally
        if player.team != self.team:
            self.reward += damages

        # -- if self hit, display new hp
        if player.index == self.index and self.render_mode_active:
            INFO_BAR.set_hp(self.hp)

        # -- if targeted player is dead
        if player.is_dead:
            print(player.name + ' IS DEAD')
            if player.team != self.team:
                self.reward += RewardList.KILL     # positive reward if not ally
            else:
                self.reward -= RewardList.KILL     # negative reward if ally

            if self.render_mode_active:
                end_game()

    # __________________________________________________________________________________________________________________
    def get_hit(self, damages: int):
        """
            get hit with some damages
        :param damages:
        :return:
        """
        self.hp -= damages
        self.reward -= damages

        if self.hp <= 0:
            self.die()

    # __________________________________________________________________________________________________________________
    def die(self):
        self.is_dead = True
        self.reward += RewardList.DIE

# ======================================================================================================================
    # INFO BAR
    def add_info(self):
        if INFO_BAR.portrait_label is None:
            INFO_BAR.init_labels(canvas)

        INFO_BAR.set_portrait(self.class_.img_path)
        INFO_BAR.set_hp(self.hp)
        INFO_BAR.set_pa(self.pa)
        INFO_BAR.set_pm(self.pm)
        self.set_spells_info_bar(self.class_.spells)

    # __________________________________________________________________________________________________________________
    def set_spells_info_bar(self, spells: list):
        self.delete_spells_info_bar()

        x = INFO_BAR.X_IMG_MIN
        y = INFO_BAR.Y_IMG_MIN

        for spell in spells:
            if x >= INFO_BAR.X_IMG_MAX:
                x = INFO_BAR.X_IMG_MIN
                y += INFO_BAR.SPELL_IMG_DIM

            self._set_spell_info_bar(spell, x, y)

            x += INFO_BAR.SPELL_IMG_DIM

    # __________________________________________________________________________________________________________________
    @staticmethod
    def delete_spells_info_bar():
        for label in INFO_BAR.spells_labels:
            label.destroy()

        INFO_BAR.tk_spells_imgs = []
        INFO_BAR.spells_labels = []

    # __________________________________________________________________________________________________________________
    def _set_spell_info_bar(self, spell: Spell, x: int, y: int):
        # -- place spell image
        tk_img = ImageTk.PhotoImage(Image.open(spell.img).resize((INFO_BAR.SPELL_IMG_DIM, INFO_BAR.SPELL_IMG_DIM)))
        label = Button(canvas, image=tk_img)
        label.config(command=lambda button=label: self.select_spell(spell.type))
        label.place(x=x, y=y, anchor=NW)

        # -- save spell label
        INFO_BAR.tk_spells_imgs.append(tk_img)
        INFO_BAR.spells_labels.append(label)

# ======================================================================================================================
    # MASKS
    def create_mask_pm(self, event=None):
        self.mask_pm = self.create_mask_range(self.box_x, self.box_y, self.pm, 'green')

    # __________________________________________________________________________________________________________________
    def delete_mask_pm(self, event=None):
        for rect in self.mask_pm:
            canvas.delete(rect)

    # __________________________________________________________________________________________________________________
    def create_mask_po(self, po):
        self.mask_po = self.create_mask_range(self.box_x, self.box_y, po, 'blue')

    # __________________________________________________________________________________________________________________
    def delete_mask_po(self):
        for rect in self.mask_po:
            canvas.delete(rect)

    # __________________________________________________________________________________________________________________
    @staticmethod
    def create_mask_range(box_x: int, box_y: int, n_box: int, color: str = 'blue'):
        mask = []

        y = (box_y - n_box) * MAP.BOX_DIM

        n_box_row = 0  # number of boxes to create on the current row
        for i in range(2 * n_box + 1):
            skip = False

            # -- do not create mask outside map
            if not MAP.BOX_HEIGHT > y // MAP.BOX_DIM >= 0:
                skip = True

            x = (box_x - n_box_row) * MAP.BOX_DIM

            if not skip:
                for j in range(2 * n_box_row + 1):
                    skip = False
                    # -- do not create mask on the player
                    if i == n_box and j == n_box_row:
                        skip = True

                    # -- do not create mask outside map
                    if not MAP.BOX_WIDTH > x // MAP.BOX_DIM >= 0:
                        skip = True

                    if not skip:
                        mask.append(canvas.create_rectangle(x, y, x + MAP.BOX_DIM, y + MAP.BOX_DIM, fill=color, outline='black'))

                    x += MAP.BOX_DIM

            if i >= n_box:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += MAP.BOX_DIM

        return mask

# ======================================================================================================================
    # UTILITY
    def place(self):
        # -- get previous position of the item
        pos = np.argwhere(MAP.matrix == self.item_value)
        if len(pos) != 0:
            # -- delete the item
            pos = pos[0]
            MAP.matrix[pos[0], pos[1]] = MapItemList.EMPTY

        # -- place the item
        MAP.place(self.box_x, self.box_y, self.item_value)

    def print(self, msg):
        if not self.print_mode_active:
            return
        color = colorama.Fore.RED if self.team == 1 else colorama.Fore.BLUE
        print(f'{color}{msg}{colorama.Fore.RESET}')


# ======================================================================================================================
    # DEPENDENT PROPS
    @property
    def x(self) -> int:
        return self.box_x * MAP.BOX_DIM

    # __________________________________________________________________________________________________________________
    @property
    def y(self) -> int:
        return self.box_y * MAP.BOX_DIM

    # __________________________________________________________________________________________________________________
    @property
    def continue_playing(self) -> bool:
        if self.num_actions_in_turn >= self.MAX_ACTIONS_IN_TURN:
            return False

        # TODO : change that (that's because IA can only cast last spell for now)
        min_pa_action = self.class_.spells[-1].pa
        if self.pm == 0 and self.pa < min_pa_action:
            return False

        return True

# ======================================================================================================================
    # ENV ACTIONS
    def get_state(self):
        return np.asarray([
            self.pa,
            self.pm,
            self.hp,
            self.po
        ])

    def do(self, action: int) -> bool:
        """
            execute action from ActionList
        :param action:
        :return: bool -> continue playing or not
        """
        self.num_actions_in_turn += 1

        if self.render_mode_active:
            time.sleep(0.5)

        if action == ActionList.END_TURN:
            self.print('END_TURN')
            # return False
            return True     # TODO : set back to FALSE

        elif action == ActionList.MOVE_LEFT:
            self.print('MOVE_LEFT')
            self.move_left()

        elif action == ActionList.MOVE_RIGHT:
            self.print('MOVE_RIGHT')
            self.move_right()

        elif action == ActionList.MOVE_UP:
            self.print('MOVE_UP')
            self.move_up()

        elif action == ActionList.MOVE_DOWN:
            self.print('MOVE_DOWN')
            self.move_down()

        elif action == ActionList.CAST_SPELL_1:
            self.auto_cast_spell(1)

        elif action == ActionList.CAST_SPELL_2:
            self.auto_cast_spell(2)

        elif action == ActionList.CAST_SPELL_3:
            self.auto_cast_spell(3)

        else:
            self.print(f'Unkown action {action}')

        return True
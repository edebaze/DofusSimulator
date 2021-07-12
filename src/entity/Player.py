from globals import *
from entity.classes import ClassList, Class
from entity.spells import SpellList, Spell
from entity.interface import info_bar
from PIL import Image, ImageTk
import time


class Player:
    def __init__(self, index: int, class_name: str):
        self.index: int = index
        self.name: str = ''
        self.class_: Class = ClassList.get(class_name)

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

        # Other
        self.is_dead: bool = False

        self.selected_spell: (None, Spell) = None       # current selected spell

# ======================================================================================================================
    # INITIALIZATION
    def create(self, pos: tuple):
        self.tk_img = ImageTk.PhotoImage(Image.open(self.class_.img_path).resize((BOX_DIM, BOX_DIM)))
        self.label = Label(can, image=self.tk_img)
        self.label.place(x=pos[0], y=pos[1], anchor=NW)

    def activate(self):
        """
            activate player bindings when his round starts
        """
        self.reset()                    # reset PA/PM
        self.add_info()                 # display player info to the info_bar
        self.set_click_key_bindings()   # set key bindings
        self.bind_movements()           # bind movement keys
        self.set_hover()                # create hover bindings

    def deactivate(self):
        """
            deactivate player when his turn ends
        """
        self.deselect_spell()
        self.label.unbind("<Enter>")
        self.label.unbind("<Leave>")

    def reset(self):
        self.pa = self.BASE_PA
        self.pm = self.BASE_PM

# ======================================================================================================================
    # CLICK BINDINGS
    def set_click_key_bindings(self):
        can.bind("<Button-1>", self.move_to_position)
        can.bind("<Button-2>", self.reset_left_click_binding)
        return

    def reset_left_click_binding(self, event=None):
        self.deselect_spell()
        can.bind("<Button-1>", self.move_to_position)

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

        box_x_selected, box_y_selected = get_selected_box(event)

        move_box_x = box_x_selected - self.box_x
        move_box_y = box_y_selected - self.box_y
        pm_used = abs(move_box_x) + abs(move_box_y)

        print(move_box_x, move_box_y)

        if pm_used > self.pm:
            print('NOT ENOUGH PM')
            return

        self.label.place(x=box_x_selected * BOX_DIM, y=box_y_selected * BOX_DIM)
        self.pm -= pm_used
        info_bar.set_pm(self.pm)

    # __________________________________________________________________________________________________________________
    def move(self):
        self.pm -= 1
        info_bar.set_pm(self.pm)

    # __________________________________________________________________________________________________________________
    def move_left(self, event=None):
        if self.pm == 0:
            return False

        x = self.label.winfo_x()

        if x - BOX_DIM < 0:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(x=x - BOX_DIM)
        self.move()

    # __________________________________________________________________________________________________________________
    def move_right(self, event=None):
        if self.pm == 0:
            return

        x = self.label.winfo_x()

        if self.x + 2 * BOX_DIM > MAP_WIDTH:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(x=x + BOX_DIM)
        self.move()

    # __________________________________________________________________________________________________________________
    def move_up(self, event=None):
        if self.pm == 0:
            return

        y = self.label.winfo_y()

        if self.y - BOX_DIM < 0:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(y=y - BOX_DIM)
        self.move()

    # __________________________________________________________________________________________________________________
    def move_down(self, event=None):
        if self.pm == 0:
            return

        y = self.label.winfo_y()

        if self.y + 2 * BOX_DIM > MAP_HEIGHT:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(y=y + BOX_DIM)
        self.move()

# ======================================================================================================================
    # ACTIONS
    def select_spell(self, spell_type: int):
        self.deselect_spell()

        spell = SpellList.get(spell_type)
        if self.pa - spell.pa < 0:
            print("can't select spell", spell.name)
            return

        self.selected_spell = spell
        can.unbind("<Button-1>")
        root.bind("<Button-1>", self.cast_spell)

        po = spell.po + int(spell.is_po_mutable) * self.po
        print('creating mask po for spell', spell.name)
        self.create_mask_po(po)

    # __________________________________________________________________________________________________________________
    def deselect_spell(self):
        if self.selected_spell is not None:
            self.selected_spell = None
            self.reset_left_click_binding()
            self.delete_mask_po()
            root.unbind('<Button-1>')

    # __________________________________________________________________________________________________________________
    def cast_spell(self, event):
        if self.selected_spell is None:
            self.deselect_spell()
            return

        # -- init absolute start position
        x_start = 0
        y_start = 0
        if isinstance(event.widget, Label):
            x_start = event.widget.winfo_x()
            y_start = event.widget.winfo_y()

        spell = self.selected_spell
        box_x_selected, box_y_selected = get_selected_box(event)
        box_x_selected += x_start // BOX_DIM
        box_y_selected += y_start // BOX_DIM

        # print(box_x_selected, box_y_selected)

        # =================================================================================
        # CHECK IS IN MAP
        if not (NUM_BOX_WIDTH > box_x_selected >= 0 and NUM_BOX_HEIGHT > box_y_selected >= 0):
            print('OUTSIDE THE MAP')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK IS IN PO
        po = spell.po + int(spell.is_po_mutable) * self.po
        num_box = abs(self.box_x - box_x_selected) + abs(self.box_y - box_y_selected)
        if num_box > po:
            print('SPELL OUT OF PO RANGE')
            self.deselect_spell()
            return

        # =================================================================================
        # CHECK IF PLAYER IS HIT
        for player in players:
            if player.box_x == box_x_selected and player.box_y == box_y_selected:
                self.hit(player)

        self.pa -= self.selected_spell.pa   # use PA
        info_bar.set_pa(self.pa)            # display use of PA in the info bar
        self.deselect_spell()

    # __________________________________________________________________________________________________________________
    def hit(self, player):
        """
            current player is hitting an other player with current selected spell
        :param player:
        :return:
        """
        damages = self.selected_spell.damages()
        player.get_hit(damages)
        print(self.selected_spell.name, ':', damages, 'hp')

        # -- if self hit, display new hp
        if player.index == self.index:
            info_bar.set_hp(self.hp)

    # __________________________________________________________________________________________________________________
    def get_hit(self, damages: int):
        """
            get hit with some damages
        :param damages:
        :return:
        """
        self.hp -= damages

        if self.hp <= 0:
            self.die()

    # __________________________________________________________________________________________________________________
    def die(self):
        self.is_dead = True
        end_game(players)

# ======================================================================================================================
    # INFO BAR
    def add_info(self):
        info_bar.set_portrait(self.class_.img_path)
        info_bar.set_hp(self.hp)
        info_bar.set_pa(self.pa)
        info_bar.set_pm(self.pm)
        self.set_spells_info_bar(self.class_.spells)

    # __________________________________________________________________________________________________________________
    def set_spells_info_bar(self, spells: list):
        self.delete_spells_info_bar()

        x = info_bar.X_IMG_MIN
        y = info_bar.Y_IMG_MIN

        for spell in spells:
            if x >= info_bar.X_IMG_MAX:
                x = info_bar.X_IMG_MIN
                y += info_bar.SPELL_IMG_DIM

            self._set_spell_info_bar(spell, x, y)

            x += info_bar.SPELL_IMG_DIM

    # __________________________________________________________________________________________________________________
    @staticmethod
    def delete_spells_info_bar():
        for label in info_bar.spells_labels:
            label.destroy()

        info_bar.tk_spells_imgs = []
        info_bar.spells_labels = []

    # __________________________________________________________________________________________________________________
    def _set_spell_info_bar(self, spell: Spell, x: int, y: int):
        # -- place spell image
        tk_img = ImageTk.PhotoImage(Image.open(spell.img).resize((info_bar.SPELL_IMG_DIM, info_bar.SPELL_IMG_DIM)))
        label = Button(root, image=tk_img)
        label.config(command=lambda button=label: self.select_spell(spell.type))
        label.place(x=x, y=y, anchor=NW)

        # -- save spell label
        info_bar.tk_spells_imgs.append(tk_img)
        info_bar.spells_labels.append(label)

# ======================================================================================================================
    # MASKS
    def create_mask_pm(self, event=None):
        self.mask_pm = self.create_mask_range(self.box_x, self.box_y, self.pm, 'green')

    # __________________________________________________________________________________________________________________
    def delete_mask_pm(self, event=None):
        for rect in self.mask_pm:
            can.delete(rect)

    # __________________________________________________________________________________________________________________
    def create_mask_po(self, po):
        self.mask_po = self.create_mask_range(self.box_x, self.box_y, po, 'blue')

    # __________________________________________________________________________________________________________________
    def delete_mask_po(self):
        for rect in self.mask_po:
            can.delete(rect)

    # __________________________________________________________________________________________________________________
    @staticmethod
    def create_mask_range(box_x: int, box_y: int, n_box: int, color: str = 'blue'):
        mask = []

        y = (box_y - n_box) * BOX_DIM

        n_box_row = 0  # number of boxes to create on the current row
        for i in range(2 * n_box + 1):
            skip = False

            # -- do not create mask outside map
            if not NUM_BOX_HEIGHT > y // BOX_DIM >= 0:
                skip = True

            x = (box_x - n_box_row) * BOX_DIM

            if not skip:
                for j in range(2 * n_box_row + 1):
                    skip = False
                    # -- do not create mask on the player
                    if i == n_box and j == n_box_row:
                        skip = True

                    # -- do not create mask outside map
                    if not NUM_BOX_WIDTH > x // BOX_DIM >= 0:
                        skip = True

                    if not skip:
                        mask.append(can.create_rectangle(x, y, x + BOX_DIM, y + BOX_DIM, fill=color, outline='black'))

                    x += BOX_DIM

            if i >= n_box:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += BOX_DIM

        return mask

# ======================================================================================================================
    # DEPENDENT PROPS
    @property
    def x(self) -> int:
        return self.label.winfo_x()

    # __________________________________________________________________________________________________________________
    @property
    def y(self) -> int:
        return self.label.winfo_y()

    # __________________________________________________________________________________________________________________
    @property
    def box_x(self) -> int:
        return self.label.winfo_x() // BOX_DIM

    # __________________________________________________________________________________________________________________
    @property
    def box_y(self) -> int:
        return self.label.winfo_y() // BOX_DIM
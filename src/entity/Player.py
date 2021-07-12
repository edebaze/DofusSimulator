from globals import *
from entity.classes import ClassList, Class
from entity.spells import SpellList, Spell
from entity.interface import info_bar
from PIL import Image, ImageTk
import time


class Player:
    def __init__(self, index: int, class_name: str):
        self.index: int  = index
        self.name: str  = ''
        self.class_: Class = ClassList.get(class_name)

        # player image
        self.tk_img = None                  # image of the player (PhotoImage object)
        self.label: (None, Label) = None    # label of the image in Canvas

        self.BASE_HP = 100          # initial HP of the player
        self.BASE_PA = 7            # initial PA of the player
        self.BASE_PM = 3            # initial PM of the player
        self.BASE_PO = 2            # initial PO of the player
        self.hp = self.BASE_HP      # current HP of the player
        self.pa = self.BASE_PA      # current PA of the player
        self.pm = self.BASE_PM      # current PM of the player
        self.po = self.BASE_PO      # current PO of the player

        self.selected_spell: (None, Spell) = None       # current selected spell

# ======================================================================================================================
    def create(self, pos: tuple):
        self.tk_img = ImageTk.PhotoImage(Image.open(self.class_.img_path).resize((BOX_DIM, BOX_DIM)))
        self.label = Label(root, image=self.tk_img)
        self.label.place(x=pos[0], y=pos[1], anchor=NW)
        # self.img = can.create_image(pos[0], pos[1], anchor=NW, image=self.tk_img)

    def activate(self):
        self.reset()
        self.add_info()
        self.set_click_key_bindings()
        self.bind_movements()
        self.create_hover()

    def deactivate(self):
        self.label.unbind("<Enter>")
        self.label.unbind("<Leave>")
        return

    def reset(self):
        self.pa = self.BASE_PA
        self.pm = self.BASE_PM

    def display_hello(self, event):
        print('Hello')

# ======================================================================================================================
    # CLICK BINDINGS
    def set_click_key_bindings(self):
        can.bind("<Button-1>", self.move_to_position)
        can.bind("<Button-2>", self.reset_left_click_binding)
        return

    def reset_left_click_binding(self, event=None):
        can.bind("<Button-1>", self.move_to_position)

# ======================================================================================================================
    # HOVER BINDINGS
    def create_hover(self):
        self.label.bind('<Enter>', self.display_hello)
        self.label.bind('<Leave>', self.display_hello)
        return

    def pm_range(self):
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

    def move_to_position(self, event):
        box_x_selected, box_y_selected = get_selected_box(event)

        move_x = box_x_selected - self.box_x
        move_y = box_y_selected - self.box_y
        print(move_x, move_y)
        if abs(move_x) + abs(move_y) > self.pm:
            print('TO FAR TO MOVE OVER THERE')
            return

        for i in range(abs(move_x)):
            if move_x > 0:
                self.move_right()
            else:
                self.move_left()

        for i in range(abs(move_y)):
            if move_y > 0:
                self.move_down()
            else:
                self.move_up()

    def move(self):
        self.pm -= 1
        info_bar.set_pm(self.pm)

    def move_left(self, event=None):
        if self.pm == 0:
            return False

        x = self.label.winfo_x()

        if x - BOX_DIM < 0:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(x=x - BOX_DIM)
        self.move()

    def move_right(self, event=None):
        if self.pm == 0:
            return

        x = self.label.winfo_x()

        if self.x + 2 * BOX_DIM > MAP_WIDTH:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(x=x + BOX_DIM)
        self.move()

    def move_up(self, event=None):
        if self.pm == 0:
            return

        y = self.label.winfo_y()

        if self.y - BOX_DIM < 0:
            print("CAN'T GO OUTSIDE THE MAP")
            return

        self.label.place(y=y - BOX_DIM)
        self.move()

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
        spell = SpellList.get(spell_type)
        if self.pa - spell.pa < 0:
            print("can't select spell", spell.name)
            return

        self.selected_spell = spell
        can.bind("<Button-1>", self.cast_spell)

    def deselect_spell(self):
        self.selected_spell = None
        self.reset_left_click_binding()

    def cast_spell(self, event):
        if self.selected_spell is None:
            self.deselect_spell()
            return

        spell = self.selected_spell
        box_x_selected, box_y_selected = get_selected_box(event)

        # CHECK IS IN PO
        po = spell.po + int(spell.is_po_mutable) * self.po
        num_box = abs(self.box_x - box_x_selected) + abs(self.box_y - box_y_selected)
        if num_box > po:
            print('TO FAR')
            self.deselect_spell()
            return

        # CHECK IF PLAYER IS HIT
        for player in players:
            if player.box_x == box_x_selected and player.box_y == box_y_selected:
                damages = self.selected_spell.damages()
                player.hp -= damages
                print(self.selected_spell.name, ':', damages, 'hp')

                # -- if self hit, display new hp
                if player.index == self.index:
                    info_bar.set_hp(self.hp)

        self.pa -= self.selected_spell.pa   # use PA
        info_bar.set_pa(self.pa)            # display use of PA in the info bar
        self.deselect_spell()

# ======================================================================================================================
    # INFO BAR
    def add_info(self):
        info_bar.set_portrait(self.class_.img_path)
        info_bar.set_hp(self.hp)
        info_bar.set_pa(self.pa)
        info_bar.set_pm(self.pm)
        self.set_spells_info_bar(self.class_.spells)

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

    @staticmethod
    def delete_spells_info_bar():
        for label in info_bar.spells_labels:
            label.destroy()

        info_bar.tk_spells_imgs = []
        info_bar.spells_labels = []

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
    # DEPENDENT PROPS
    @property
    def x(self) -> int:
        return self.label.winfo_x()

    @property
    def y(self) -> int:
        return self.label.winfo_y()

    @property
    def box_x(self) -> int:
        return self.label.winfo_x() // BOX_DIM

    @property
    def box_y(self) -> int:
        return self.label.winfo_y() // BOX_DIM
from game.actions.ActionList import ActionList
from game.spells import Spell, SpellDirectionList
from game.spells.Spell import Spell
from game.map import MapItemList, Map
from game.interface import InfoBar
from game.Engine import Engine

from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import time
import pdb


class GUI:
    SLEEP_TIME = 0.1

    def __init__(self, engine: Engine):
        self.engine: Engine = engine
        self.root = None
        self.canvas = None

        self.info_bar: InfoBar = InfoBar(self.map)

        self.destroy_at_end_game: bool = True   # destroy tk window when game is ending
        self.is_destroyed: bool = False         # destroy tk window when game is ending
        self.mask_pm: list = []                 # mask for pm (constraining all ids of rect)
        self.mask_spell: list = []              # mask for po (constraining all ids of rect)
        self.mask_spell_zone: list = []         # mask for zone of the spell

# ======================================================================================================================
    # ENV METHODS
    def reset(self):
        self.root = Tk()
        self.canvas = Canvas(self.root, width=self.map.WIDTH + self.map.PADDING, height=self.map.HEIGHT + self.info_bar.HEIGHT, bg='white')
        self.is_destroyed = False

        # -------------------------------------------------------------
        # RESET CONTROLS
        self.set_key_bindings()

        # -------------------------------------------------------------
        # RESET DISPLAY MAP AND INFO_BAR
        self.display_map()
        self.info_bar = InfoBar(self.map)
        self.info_bar.init_labels(self.canvas)

        # -------------------------------------------------------------
        # RESET PLAYERS
        for player in self.engine.players:
            player.print_mode_active = True
            self.display_player(player)
        self.activate_player(self.engine.current_player)

    def render(self):
        self.root.after(1, self.play_game())

        self.root.mainloop()

        player_1 = self.engine.players[0]
        player_2 = self.engine.players[1]

        print(f'PLAYER 1 score : {player_1.score}')
        print(f'PLAYER 2 score : {player_2.score}')

    def update(self):
        # RENDERING
        for player in self.engine.players:
            self.display_move(player)

        player = self.engine.current_player
        self.info_bar.set_hp(player.hp)
        self.info_bar.set_pa(player.pa)
        self.info_bar.set_pm(player.pm)
        self.deselect_spell()

        self.root.update()

# ======================================================================================================================
    # MAP RENDERING
    def display_map(self):
        """
             display the map to the GUI
         :param canvas: object of class Canvas
        """
        canvas = self.canvas

        y = 0
        for row in self.map.matrix:
            x = 0
            for box_content in row:
                color = 'white' if ((x + y) // self.map.BOX_DIM) % 2 == 0 else 'grey'

                if box_content[self.map.item_void_index] == 1:
                    color = 'black'

                if box_content[self.map.item_block_index] == 1:
                    color = 'yellow'

                canvas.create_rectangle(x, y, x + self.map.BOX_DIM, y + self.map.BOX_DIM, fill=color, outline='black')
                x += self.map.BOX_DIM

            y += self.map.BOX_DIM

        canvas.pack()

    def place_player(self, player):
        self.info_bar.set_pm(player.pm)
        player.label.place(x=player.box_x * self.map.BOX_DIM, y=player.box_y * self.map.BOX_DIM)

# ======================================================================================================================
    # KEY BINDING
    def set_key_bindings(self):
        self.root.bind("<space>", self.end_turn)
        self.root.bind('<Return>', self.switch_player_1)
        self.bind_movements()

    def set_click_key_bindings(self):
        self.canvas.bind("<Button-1>", self.move_to_position)
        self.root.bind("<Button-3>", self.map.display_box_content)

    def set_hover(self, player):
        player.label.bind('<Enter>', self.create_mask_pm)
        player.label.bind('<Leave>', self.delete_mask_pm)

    def bind_movements(self):
        """
            bind movement keys
        :return:
        """
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Up>', self.move_up)
        self.root.bind('<Down>', self.move_down)

# ======================================================================================================================
    # TURNS
    def play_game(self):
        self.play_turn()

    def play_turn(self):
        print('==================================================')
        print(f'TURN {self.engine.turn} with PLAYER {self.engine.current_player.index}')

        if self.engine.current_player.agent.is_activated:
            continue_playing = True
            while continue_playing:
                continue_playing = self.play_action()

                if self.engine.get_done():
                    self.end_game()
                    return

            self.end_turn()

    # __________________________________________________________________________________________________________________
    def end_turn(self, event=None):
        # -- end turn in the engine
        self.engine.end_turn()

        if self.engine.get_done():
            self.end_game()
            return

        # -- GUI displaying of a turn ending
        self.activate_player(self.engine.current_player)
        for player in self.engine.players:
            if player.index != self.engine.current_player:
                self.deactivate_player(player)

        # -- go to next turn
        if self.engine.current_player.agent.is_activated:
            self.root.after(1, self.play_turn())

    # __________________________________________________________________________________________________________________
    def play_action(self, action=None):
        agent = self.engine.current_player.agent
        if agent.is_activated:
            self.sleep()

        continue_playing = self.engine.play_action(action)
        self.update()

        return continue_playing

    # __________________________________________________________________________________________________________________
    def end_game(self):
        if self.root is None or self.is_destroyed:
            return

        if self.destroy_at_end_game:
            self.is_destroyed = True
            self.root.destroy()
            return

        player = None
        for player in self.engine.players:
            if not player.is_dead:
                break

        popup = Toplevel()
        popup.title('game over')

        text = f"GAME OVER ! \n Player {player.index} WON !"
        end_label = Label(popup, text=text, bg="black", fg="white", width=20, height=10)
        end_label.config(font=("Courier", 32, "italic"))
        end_label.pack()

        Button(popup, text='Quit', command=self.root.destroy).pack(padx=10, pady=10)
        Button(popup, text='Restart', command=self.reset).pack(padx=10, pady=10)

# ======================================================================================================================
    # MOVE
    def reset_left_click_binding(self, event=None):
        self.engine.current_player.deselect_spell()
        self.canvas.bind("<Button-1>", self.move_to_position)

    # __________________________________________________________________________________________________________________
    def move_to_position(self, event):
        """
            move player to selected position
        :param event:
        :return:
        """
        player = self.engine.current_player
        box_x, box_y = self.map.get_selected_box(event)

        self.engine.move_to_position(player, box_x, box_y)
        self.display_move(player)

    def move_left(self, event):
        self.play_action(ActionList.MOVE_LEFT)

    def move_right(self, event):
        self.play_action(ActionList.MOVE_RIGHT)

    def move_up(self, event):
        self.play_action(ActionList.MOVE_UP)

    def move_down(self, event):
        self.play_action(ActionList.MOVE_DOWN)

    def display_move(self, player):
        self.info_bar.set_pm(self.engine.current_player.pm)
        self.place_player(player)
        self.root.update()

# ======================================================================================================================
    # SPELL
    def auto_cast_spell(self, spell: Spell, event=None):
        spells = self.engine.current_player.class_.spells
        for i in range(len(spells)):
            if spell.id == spells[i].id:
                action = ActionList.get_cast_spell(i)
                self.play_action(action)

    # __________________________________________________________________________________________________________________
    def select_spell(self, spell: Spell):
        self.engine.select_spell(spell)

        # -- display selected spell po
        if self.engine.current_player.selected_spell is not None:
            self.canvas.unbind("<Button-1>")
            self.root.bind("<Button-1>", self.cast_spell)
            self.create_mask_spell()

    # __________________________________________________________________________________________________________________
    def deselect_spell(self, envent=None):
        self.engine.deselect_spell()
        self.reset_left_click_binding()
        self.delete_mask_spell()
        self.root.unbind('<Button-1>')

    # __________________________________________________________________________________________________________________
    def cast_spell(self, event):
        box_x, box_y = self.map.get_selected_box(event)
        self.engine.cast_spell(box_x, box_y)
        self.info_bar.set_pa(self.engine.current_player.pa)     # display use of PA in the info bar
        self.info_bar.set_hp(self.engine.current_player.hp)     # refresh HP
        self.deselect_spell()

        self.update()

# ======================================================================================================================
    # PLAYER FUNCTIONS
    def display_player(self, player):
        player.tk_img = ImageTk.PhotoImage(
            Image.open(player.class_.img_path).resize((self.map.BOX_DIM, self.map.BOX_DIM)))
        player.label = Label(self.canvas, image=player.tk_img)
        player.label.place(x=player.x, y=player.y, anchor=NW)

        self.root.update()

    # __________________________________________________________________________________________________________________
    def activate_player(self, player):
        self.add_info(player)           # display player info to the info_bar
        self.set_click_key_bindings()   # set key bindings
        self.bind_movements()           # bind movement keys
        self.set_hover(player)          # create hover bindings

    # __________________________________________________________________________________________________________________
    def deactivate_player(self, player):
        self.deselect_spell(player)
        player.label.unbind("<Enter>")
        player.label.unbind("<Leave>")

    # __________________________________________________________________________________________________________________
    def add_info(self, player):
        if self.info_bar.portrait_label is None:
            self.info_bar.init_labels(self.canvas)

        self.info_bar.set_portrait(player.class_.img_path)
        self.info_bar.set_hp(player.hp)
        self.info_bar.set_pa(player.pa)
        self.info_bar.set_pm(player.pm)
        self.set_spells_info_bar(player.class_.spells)

    # __________________________________________________________________________________________________________________
    def set_spells_info_bar(self, spells: list):
        self.delete_spells_info_bar()

        x = self.info_bar.X_IMG_MIN
        y = self.info_bar.Y_IMG_MIN

        for spell in spells:
            if x >= self.info_bar.X_IMG_MAX:
                x = self.info_bar.X_IMG_MIN
                y += self.info_bar.SPELL_IMG_DIM

            self._set_spell_info_bar(spell, x, y)

            x += self.info_bar.SPELL_IMG_DIM

    # __________________________________________________________________________________________________________________
    def delete_spells_info_bar(self):
        for label in self.info_bar.spells_labels:
            label.destroy()

        self.info_bar.tk_spells_imgs = []
        self.info_bar.spells_labels = []

    # __________________________________________________________________________________________________________________
    def _set_spell_info_bar(self, spell, x: int, y: int):
        # -- place spell image
        tk_img = ImageTk.PhotoImage(Image.open(spell.img).resize((self.info_bar.SPELL_IMG_DIM, self.info_bar.SPELL_IMG_DIM)))
        label = Button(self.canvas, image=tk_img)
        # label.config(command=lambda button=label: self.select_spell(spell))
        label.config(command=lambda button=label: self.select_spell(spell))
        label.place(x=x, y=y, anchor=NW)

        # -- save spell label
        self.info_bar.tk_spells_imgs.append(tk_img)
        self.info_bar.spells_labels.append(label)

        self.root.update()

    # __________________________________________________________________________________________________________________
    def switch_player_1(self, event):
        self.engine.players[0].agent.is_activated = not self.engine.players[0].agent.is_activated

# ======================================================================================================================
    # MASKS
    def create_mask_pm(self, event=None):
        positions = self.map.get_item_positions(MapItemList.MASK_PM)
        mask = []
        for pos in positions:
            x = pos[0] * self.map.BOX_DIM
            y = pos[1] * self.map.BOX_DIM
            rect = self.canvas.create_rectangle(x, y, x + self.map.BOX_DIM, y + self.map.BOX_DIM, fill='green', outline='black')
            self.canvas.tag_bind(rect, '<Enter>', self.create_mask_spell_zone)
            mask.append(rect)

        self.mask_pm = mask

    # __________________________________________________________________________________________________________________
    def delete_mask_pm(self, event=None):
        for rect in self.mask_pm:
            self.canvas.delete(rect)

    # __________________________________________________________________________________________________________________
    def create_mask_spell(self):
        positions = self.map.get_item_positions(MapItemList.MASK_SPELL)
        mask = []
        for pos in positions:
            x = pos[0] * self.map.BOX_DIM
            y = pos[1] * self.map.BOX_DIM
            rect = self.canvas.create_rectangle(x, y, x + self.map.BOX_DIM, y + self.map.BOX_DIM, fill='blue', outline='black')
            self.canvas.tag_bind(rect, '<Enter>', self.create_mask_spell_zone)
            self.canvas.tag_bind(rect, '<Leave>', self.delete_mask_spell_zone)
            mask.append(rect)

        self.mask_spell = mask

    # __________________________________________________________________________________________________________________
    def delete_mask_spell(self):
        for rect in self.mask_spell:
            self.canvas.delete(rect)

    # __________________________________________________________________________________________________________________
    def create_mask_spell_zone(self, event):
        spell = self.engine.current_player.selected_spell
        box_x, box_y = self.map.get_selected_box(event)

        x_player = self.engine.current_player.box_x
        y_player = self.engine.current_player.box_y

        # -- orientate spell target matrix according to spell direction
        spell_direction = SpellDirectionList.get_direction(box_x, box_y, x_player, y_player)
        spell_zone = SpellDirectionList.orientate_spell(spell.zone, spell_direction)

        # -- place center of spell on selected box
        zone_center = np.argwhere(spell_zone == Spell.ZONE_CENTER)
        zone_ranges = np.argwhere(spell_zone == Spell.ZONE_RANGE)
        zone_ranges = np.concatenate([zone_ranges, zone_center])

        for zone_range in zone_ranges:
            x = (zone_range[0] + box_x - zone_center[0, 0]) * self.map.BOX_DIM
            y = (zone_range[1] + box_y - zone_center[0, 1]) * self.map.BOX_DIM

            rect = self.canvas.create_rectangle(x, y, x + self.map.BOX_DIM, y + self.map.BOX_DIM, fill='red', outline='black')
            self.mask_spell_zone.append(rect)

        self.root.update()

    # __________________________________________________________________________________________________________________
    def delete_mask_spell_zone(self, event=None):
        for rect in self.mask_spell_zone:
            self.canvas.delete(rect)
        self.root.update()

    # __________________________________________________________________________________________________________________
    def create_mask_range(self, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 0, color: str = 'blue'):
        mask = []

        y = (box_y - n_box_max) * self.map.BOX_DIM

        n_box_row = 0  # number of boxes to create on the current row
        for i in range(2 * n_box_max + 1):
            skip = False

            # -- do not create mask outside map
            if not self.map.BOX_HEIGHT > y // self.map.BOX_DIM >= 0:
                skip = True

            x = (box_x - n_box_row) * self.map.BOX_DIM

            if not skip:
                for j in range(2 * n_box_row + 1):
                    skip = False
                    # -- do not create mask on the player
                    if i == n_box_max and j == n_box_row:
                        skip = True

                    # -- do not create mask outside map
                    if not self.map.BOX_WIDTH > x // self.map.BOX_DIM >= 0:
                        skip = True

                    # -- do not create mask in MIN PO
                    if abs(i - n_box_max) + abs(j - n_box_row) <= n_box_min:
                        skip = True

                    if not skip:
                        mask.append(self.canvas.create_rectangle(x, y, x + self.map.BOX_DIM, y + self.map.BOX_DIM, fill=color, outline='black'))

                    x += self.map.BOX_DIM

            if i >= n_box_max:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += self.map.BOX_DIM

        return mask

    # __________________________________________________________________________________________________________________
    def create_mask_line(self, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 0, color: str = 'blue'):
        mask = []

        y = (box_y - n_box_max) * self.map.BOX_DIM

        n_box_row = 0  # number of boxes to create on the current row
        for i in range(2 * n_box_max + 1):
            skip = False

            # -- do not create mask outside map
            if not self.map.BOX_HEIGHT > y // self.map.BOX_DIM >= 0:
                skip = True

            x = (box_x - n_box_row) * self.map.BOX_DIM

            if not skip:
                for j in range(2 * n_box_row + 1):
                    skip = False
                    # -- do not create mask on the player
                    if i == n_box_max and j == n_box_row:
                        skip = True

                    # -- do not create mask outside map
                    if not self.map.BOX_WIDTH > x // self.map.BOX_DIM >= 0:
                        skip = True

                    if not skip:
                        mask.append(self.canvas.create_rectangle(x, y, x + self.map.BOX_DIM, y + self.map.BOX_DIM, fill=color, outline='black'))

                    x += self.map.BOX_DIM

            if i >= n_box_max:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += self.map.BOX_DIM

        return mask

# ======================================================================================================================
    # UTILITY
    @staticmethod
    def sleep(t=SLEEP_TIME):
        time.sleep(t)

# ======================================================================================================================
    # DEPENDENT PROPERTIES
    @property
    def map(self) -> Map:
        return self.engine.map
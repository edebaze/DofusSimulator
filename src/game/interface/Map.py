from game.interface.MapItemList import MapItemList
from tkinter import Label
import pdb
import numpy as np
import random


class Map:
    BOX_DIM = 50
    PADDING = 200

    def __init__(self, map_number: int = 0):
        self.map_number: int    = map_number
        self.matrix: np.ndarray = np.empty(0)

        self.BOX_WIDTH: int     = 0
        self.BOX_HEIGHT: int    = 0
        self.WIDTH: int         = 0
        self.HEIGHT: int        = 0

        self.create()

    def create(self):
        self.matrix = self.load_map(self.map_number)

        self.BOX_WIDTH = len(self.matrix[0])
        self.BOX_HEIGHT = len(self.matrix)
        self.WIDTH = self.BOX_WIDTH * self.BOX_DIM
        self.HEIGHT = self.BOX_HEIGHT * self.BOX_DIM

    def display(self, canvas):
        y = 0
        for row in self.matrix:
            x = 0
            for block in row:
                color = 'white' if ((x + y) // self.BOX_DIM) % 2 == 0 else 'grey'

                if block == MapItemList.VOID:
                    color = 'black'

                if block == MapItemList.BLOCK:
                    color = 'red'

                canvas.create_rectangle(x, y, x + self.BOX_DIM, y + self.BOX_DIM, fill=color, outline='black')
                x += self.BOX_DIM

            y += self.BOX_DIM

        canvas.pack()

    def place(self, box_x, box_y, item):
        if not self.is_empty(box_x, box_y):
            return
        self.matrix[box_y][box_x] = item

    def box(self, box_x, box_y):
        if box_x >= len(self.matrix[0]) or box_y >= len(self.matrix):
            return None
        return self.matrix[box_y][box_x]

    def is_empty(self, box_x, box_y):
        box_content = self.box(box_x, box_y)
        return box_content == MapItemList.EMPTY or box_content is None

    def show(self):
        print(self.matrix)

    def get_initial_player_placement(self, team):
        min_x = 1
        max_x = self.BOX_WIDTH - 2
        if team == 1:
            min_y = self.BOX_HEIGHT - 3
            max_y = self.BOX_HEIGHT - 2
        elif team == 2:
            min_y = 1
            max_y = 2
        else:
            print('ERROR placing player of team', team)

        box_x = random.randint(min_x, max_x)
        box_y = random.randint(min_y, max_y)

        while not self.is_empty(box_x, box_y):
            box_x = random.randint(min_x, max_x)
            box_y = random.randint(min_y, max_y)

        return box_x, box_y

    def place_player(self, player):
        # -- get previous position of the item
        pos = np.argwhere(self.matrix == player.item_value)
        if len(pos) != 0:
            # -- delete the item
            pos = pos[0]
            self.matrix[pos[0], pos[1]] = MapItemList.EMPTY

        # -- place the item
        self.place(player.box_x, player.box_y, player.item_value)

    def get_box_content(self, event):
        x, y = self.get_selected_box(event)
        content = self.box(x, y)
        print(f'(x={x}, y={y}) : {content}')

    @staticmethod
    def get_selected_box(event):
        """
            get coordinates of selected box
        :param event:
        :return:
        """

        # -- init absolute start position
        x_start = 0
        y_start = 0
        if isinstance(event.widget, Label):
            x_start = event.widget.winfo_x()
            y_start = event.widget.winfo_y()

        x = (event.x + x_start) // Map.BOX_DIM
        y = (event.y + y_start) // Map.BOX_DIM

        return x, y

    @staticmethod
    def load_map(map_number):
        from ressources.maps import all_maps
        return all_maps[map_number]
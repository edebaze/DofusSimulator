from game.map.MapItemList import MapItemList
from tkinter import Label
import numpy as np
import random
import copy


class Map:
    BOX_DIM = 50
    PADDING = 200

    def __init__(self, map_number: int = 0):
        self.map_number: int    = map_number    # map to load's number
        self.matrix: np.ndarray = np.empty(0)   # matrix of the map, containing each item values

        self.BOX_WIDTH: int     = 0         # number of boxes on x
        self.BOX_HEIGHT: int    = 0         # number of boxes on y
        self.WIDTH: int         = 0         # map width in pixel
        self.HEIGHT: int        = 0         # map height in pixel

        self.create()

    def create(self):
        """
            create the map matrix and update the params :
                BOX_WIDTH = number of boxes on x
                BOX_HEIGHT = number of boxes on y
                WIDTH = map width in pixel
                HEIGHT = map height in pixel
        """
        self.matrix = self.load_map(self.map_number)

        self.BOX_WIDTH = len(self.matrix[0])
        self.BOX_HEIGHT = len(self.matrix)
        self.WIDTH = self.BOX_WIDTH * self.BOX_DIM
        self.HEIGHT = self.BOX_HEIGHT * self.BOX_DIM

    def get_state(self) -> np.ndarray:
        matrix = copy.copy(self.matrix)
        indexes = np.argwhere(matrix <= max(MapItemList.MAP_BOX))  # get indexes of the box items
        matrix[:] = 0               # set everything to 0
        for index in indexes:       # set position of the item to 1
            matrix[tuple(index)] = 1
        state = matrix.reshape(matrix.shape[0] * matrix.shape[1])

        for item_value in MapItemList.get_item_values():
            # -- skip box instances
            if item_value in MapItemList.MAP_BOX:
                continue

            matrix = copy.copy(self.matrix)                 # copy map matrix
            indexes = np.argwhere(matrix == item_value)     # get indexes of the item
            matrix[:] = 0                                   # set everything to 0
            for index in indexes:                           # set position of the item to 1
                matrix[tuple(index)] = 1

            matrix = matrix.reshape(matrix.shape[0] * matrix.shape[1])  # reshape matrix to 1D vector
            state = np.concatenate([state, matrix])         # add item matrix to the general state of the map

        return state

    def place(self, box_x, box_y, item) -> None:
        """
            place the value of an item on the map at requested coordinates
        :param box_x: x coordinates of the box
        :param box_y: y coordinates of the box
        :param item: value of the item (cf: MapItemList)
        """
        if not self.is_empty(box_x, box_y):
            return
        self.matrix[box_y][box_x] = item

    def box(self, box_x, box_y) -> (None, int):
        """
            get the content of the box

        :param box_x: x coordinates of the box
        :param box_y: y coordinates of the box
        :return:
            None : the box is not in the map
            int : value of the content of the box (cf: MapItemList)
        """
        if box_x >= len(self.matrix[0]) or box_y >= len(self.matrix):
            return None
        return self.matrix[box_y][box_x]

    def is_empty(self, box_x, box_y) -> bool:
        """
            is the selected box empty

        :param box_x: x coordinates of the box
        :param box_y: y coordinates of the box
        :return: True if the box is empty
        """
        box_content = self.box(box_x, box_y)
        return box_content == MapItemList.EMPTY or box_content is None

    def get_initial_player_placement(self, team):
        """
            get the initial box placement of a player according to his team

        :param team: team of the player
        :return: box_x : x coordinates of the box
        :return: box_y: y coordinates of the box
        """
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
            return

        # -- choose random box
        box_x = random.randint(min_x, max_x)
        box_y = random.randint(min_y, max_y)

        # -- reposition element as long as the selected box is not empty
        while not self.is_empty(box_x, box_y):
            box_x = random.randint(min_x, max_x)
            box_y = random.randint(min_y, max_y)

        return box_x, box_y

    def place_player(self, player):
        """
            place the item_value (MapItemList) of a Player on the map's matrix

        :param player: object of class Player
        """
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

    def show(self):
        """ show the matrix in the console """
        print(self.matrix)

    def generate_random_map(self):
        matrix = np.zeros((self.BOX_WIDTH, self.BOX_HEIGHT))

        # -- set map borders
        matrix[0, :] = 1
        matrix[:, 0] = 1
        matrix[:, -1] = 1
        matrix[-1, :] = 1

        for i in range(self.BOX_WIDTH):
            for j in range(self.BOX_HEIGHT):
                continue

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
    def load_map(map_number: int) -> np.ndarray:
        """
            load a map matrix from maps.py file
        :param map_number: number of the map to load
        :return:
        """
        from game.map.maps import all_maps
        return all_maps[map_number]
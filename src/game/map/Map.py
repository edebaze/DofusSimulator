from game.map.maps import all_maps
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

        # ITEM VALUES (stock here to avoid recalculation)
        self.item_values: list  = MapItemList.get_item_values()                 # list of all item_values
        self.item_empty_index: int = self.item_values.index(MapItemList.EMPTY)  # index of item value empty
        self.item_void_index: int = self.item_values.index(MapItemList.VOID)    # index of item value void
        self.item_block_index: int = self.item_values.index(MapItemList.BLOCK)   # index of item value block

        self.BOX_WIDTH: int     = 0         # number of boxes on x
        self.BOX_HEIGHT: int    = 0         # number of boxes on y
        self.WIDTH: int         = 0         # map width in pixel
        self.HEIGHT: int        = 0         # map height in pixel

        self.create()

########################################################################################################################
    # INITIALIZATION
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

    # __________________________________________________________________________________________________________________
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

########################################################################################################################
    # ENV METHODS
    def get_state(self) -> np.ndarray:
        return self.matrix

########################################################################################################################
    # PLACE / REMOVE ITEMS ON POSITIONS
    def place(self, box_x, box_y, item_value) -> None:
        """
            place the value of an item on the map at requested coordinates
        :param box_x: x coordinates of the box
        :param box_y: y coordinates of the box
        :param item_value: value of the item (cf: MapItemList)
        """
        if not self.is_empty(box_x, box_y):
            return

        index_item = self.item_values.index(item_value)

        self.matrix[box_y][box_x][index_item] = 1               # set index of item_value to 1
        self.matrix[box_y][box_x][self.item_empty_index] = 0    # set EMPTY to 0

    # __________________________________________________________________________________________________________________
    def place_player(self, player, flag_set_mask_pm: bool = True):
        """
            place the item_value (MapItemList) of a Player on the map's matrix

        :param player: object of class Player
        :param flag_set_mask_pm: create mask pm for player
        """
        # -- get previous position of the item
        box_x, box_y = self.get_item_position(player.item_value)
        if box_x is not None:
            # -- delete the item
            self.remove_item_position(box_x=box_x, box_y=box_y, item_value=player.item_value)

        # -- place the player's item_value
        self.place(player.box_x, player.box_y, player.item_value)

        # -- set player's PM mask
        if flag_set_mask_pm:
            self.remove_player_mask_pm()        # reset previous mask pm
            self.create_player_mask_pm(player)

    # __________________________________________________________________________________________________________________
    def remove_item_position(self, box_x, box_y, item_value):
        """ remove an item_value from a position in the map's matrix """
        self.matrix[box_y, box_x, self.item_values.index(item_value)] = 0   # remove item_value from position
        self.matrix[box_y, box_x, self.item_empty_index] = 1                # set box as empty

########################################################################################################################
    # CREATE / DELETE MASKS
    def create_player_mask_pm(self, player):
        """ set mask pm of player """
        self.create_mask_range(
            item_value=MapItemList.MASK_PM,
            box_x=player.box_x,
            box_y=player.box_y,
            n_box_max=player.pm
        )

    # __________________________________________________________________________________________________________________
    def create_spell_mask(self, player):
        spell = player.selected_spell
        if spell is None:
            return

        max_po = spell.max_po + spell.is_po_mutable * player.po
        if spell.is_line:
            self.create_mask_line(
                item_value=MapItemList.MASK_SPELL,
                box_x=player.box_x,
                box_y=player.box_y,
                n_box_max=max_po,
                n_box_min=spell.min_po
            )
        else:
            self.create_mask_range(
                item_value=MapItemList.MASK_SPELL,
                box_x=player.box_x,
                box_y=player.box_y,
                n_box_max=max_po,
                n_box_min=spell.min_po
            )

    # __________________________________________________________________________________________________________________
    def create_mask_range(self, item_value: int, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 0):
        """
            create a mask on the map

        :param item_value: value of the mask item in MapItemList
        :param box_x: center of the mask on x
        :param box_y: center of the mask on y
        :param n_box_max: max size of the mask
        :param n_box_min: min size of the mask
        :return:
        """

        item_index = self.item_values.index(item_value)
        y = box_y - n_box_max

        n_box_row = 0  # number of boxes to create on the current row
        for _ in range(2 * n_box_max + 1):
            skip = False

            # -- do not create mask outside map
            if not self.BOX_HEIGHT > y >= 0:
                skip = True

            x = box_x - n_box_row

            if not skip:
                for _ in range(2 * n_box_row + 1):
                    skip = False
                    # -- block, void or outside the map
                    box_content = self.box_content(x, y)
                    if box_content is None:         # check is in map
                        skip = True
                    elif box_content[self.item_block_index] == 1:   # check is block
                        skip = True
                    elif box_content[self.item_void_index] == 1:    # check is void
                        skip = True

                    # -- do not create mask in MIN PO
                    if abs(y - box_y) + abs(x - box_x) < n_box_min:
                        skip = True

                    if not skip:
                        self.matrix[y, x, item_index] = 1

                    x += 1

            if y >= box_y:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += 1

    # __________________________________________________________________________________________________________________
    def create_mask_line(self, item_value: int, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 0):
        """
            create a line mask on the map

        :param item_value: value of the mask item in MapItemList
        :param box_x: center of the mask on x
        :param box_y: center of the mask on y
        :param n_box_max: max size of the mask
        :param n_box_min: min size of the mask
        :return:
        """
        item_index = self.item_values.index(item_value)
        y = box_y - n_box_max

        n_box_row = 0  # number of boxes to create on the current row
        for _ in range(2 * n_box_max + 1):
            skip = False

            # -- do not create mask outside map
            if not self.BOX_HEIGHT > y >= 0:
                skip = True

            x = box_x - n_box_row

            if not skip:
                for _ in range(2 * n_box_row + 1):
                    skip = False
                    # -- do not create mask outside map
                    if not self.BOX_WIDTH > x >= 0:
                        skip = True

                    # -- do not create mask in MIN PO
                    if abs(y - n_box_max) + abs(x - n_box_row) < n_box_min:
                        skip = True

                    if not self.is_empty(x, y):
                        skip = True

                    if not skip:
                        self.matrix[y, x, item_index] = 1

                    x += 1

            if x > box_x + n_box_max:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += 1

    # __________________________________________________________________________________________________________________
    def remove_mask(self, item_value):
        """ remove current mask pm """
        index_mask = self.item_values.index(item_value)
        self.matrix[:, :, index_mask] = 0

    # __________________________________________________________________________________________________________________
    def remove_player_mask_pm(self):
        """ remove current mask pm """
        self.remove_mask(MapItemList.MASK_PM)

########################################################################################################################
    # BOX CONTENT
    def box_content(self, box_x, box_y) -> (None, np.ndarray):
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

    # __________________________________________________________________________________________________________________
    def is_empty(self, box_x, box_y) -> bool:
        """
            is the selected box empty

        :param box_x: x coordinates of the box
        :param box_y: y coordinates of the box
        :return: True if the box is empty
        """
        box_content = self.box_content(box_x, box_y)
        return box_content is not None and box_content[self.item_empty_index] == 1

    # __________________________________________________________________________________________________________________
    def get_item_position(self, item_value: int) -> (None, tuple):
        """
            get position (box_x, box_y) of an item
        :param item_value:
        :return:
        """
        positions = self.get_item_positions(item_value)

        if len(positions) == 0:
            return None, None

        if len(positions) > 1:
            print('Error : item_value', item_value, 'found', len(positions), 'times but must be unique')

        return tuple(positions[0])

    # __________________________________________________________________________________________________________________
    def get_item_positions(self, item_value: int) -> np.ndarray:
        """
            get array of positions (box_x, box_y) of an item

        :param item_value:
        :return:
        """
        index_item = self.item_values.index(item_value)
        positions = np.argwhere(self.matrix[:, :, index_item] == 1)
        return positions[:, ::-1]   # !!! do not forget to reverse positions to return box_x box_y

########################################################################################################################
    # DEBUG
    def get_box_content(self, event):
        """
            TKINTER debug function : display content of clicked box
        :param event:
        :return:
        """
        x, y = self.get_selected_box(event)
        content = self.box_content(x, y)
        print(f'(x={x}, y={y}) : {content}')

    # __________________________________________________________________________________________________________________
    def get2Dmatrix(self):
        """ return matrix as 2D object (with only item_values and without masks)"""
        # TODO
        return

    # __________________________________________________________________________________________________________________
    def show(self):
        """ show full matrix in the console """
        print(self.matrix)

    # __________________________________________________________________________________________________________________
    def show_item(self, item_value):
        matrix = np.zeros((self.BOX_HEIGHT, self.BOX_WIDTH))

        for pos in self.get_item_positions(item_value):
            # -- don't forget to reverse x, y in matrix
            matrix[tuple(pos[::-1])] = 1

        print(matrix)

    # __________________________________________________________________________________________________________________
    def show2D(self):
        """ show the matrix as 2D map in the console """
        print(self.get2Dmatrix())

    # __________________________________________________________________________________________________________________
    def generate_random_map(self):
        # TODO !
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

        box_x = (event.x + x_start) // Map.BOX_DIM
        box_y = (event.y + y_start) // Map.BOX_DIM

        return box_x, box_y

    @staticmethod
    def load_map(map_number: int) -> np.ndarray:
        """
            load a map matrix from maps.py file
        :param map_number: number of the map to load
        :return:
        """
        item_values = MapItemList.get_item_values()
        map = all_maps[map_number]

        h = len(map)
        w = len(map[0])
        new_map = np.zeros((w, h, len(item_values)))

        for i in range(len(map)):
            row = map[i]
            for j in range(len(row)):
                item_value = row[j]
                index_item = item_values.index(item_value)
                new_map[i, j, index_item] = 1

        return new_map
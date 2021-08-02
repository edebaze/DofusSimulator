from game.map.maps import all_maps
from game.map.MapItemList import MapItemList

from tkinter import Label
import numpy as np
import random
import copy


class Map:
    BOX_DIM = 50
    PADDING = 200
    MAX_SIZE = 20

    def __init__(self, map_number: (None, int) = 0):
        self.map_number: (None, int)    = map_number    # map to load's number
        self.matrix: np.ndarray         = np.empty(0)   # matrix of the map, containing each item values

        # ITEM VALUES (stock here to avoid recalculation)
        self.item_values: list  = MapItemList.get_item_values()                 # list of all item_values
        self.item_empty_index: int = self.item_values.index(MapItemList.EMPTY)  # index of item value empty
        self.item_void_index: int = self.item_values.index(MapItemList.VOID)    # index of item value void
        self.item_block_index: int = self.item_values.index(MapItemList.BLOCK)   # index of item value block

        self.BOX_WIDTH: int     = 0         # number of boxes on x
        self.BOX_HEIGHT: int    = 0         # number of boxes on y

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
        if self.map_number is not None:
            self.matrix = self.load_map(self.map_number)

            self.BOX_WIDTH = len(self.matrix[0])
            self.BOX_HEIGHT = len(self.matrix)

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
            print(f'ERROR team ({team}) is not == 1 or == 2')
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

    def get_spell_state(self, box_x, box_y, max_range, enemy_player_item_value) -> np.ndarray:
        """
            Create a mini matrix of map containing relevant info for the spell to cast
                -> complete out of map
        :param box_x:
        :param box_y:
        :param max_range:
        :param enemy_player_item_value:
        :return:
        """

        IS_ENEMY = 0
        item_values = [IS_ENEMY, MapItemList.MASK_SPELL]

        # -- set index of items
        index_is_enemy = item_values.index(IS_ENEMY)
        index_mask_spell = item_values.index(MapItemList.MASK_SPELL)

        # -- index of the enemy and mask_spell in the global item_values list
        global_enemy_index = self.item_values.index(enemy_player_item_value)
        global_mask_spell_index = self.item_values.index(MapItemList.MASK_SPELL)

        matrix = np.zeros((max_range, max_range, len(item_values)))

        x = box_x - max_range
        y = box_y - max_range

        for _ in range(len(max_range) * 2 + 1):
            for _ in range(len(max_range) * 2 + 1):
                box_content = self.box_content(x, y)
                if box_content is not None:
                    matrix[y, x, index_is_enemy] = box_content[global_enemy_index]
                    matrix[y, x, index_mask_spell] = box_content[global_mask_spell_index]

                x += 1
            y += 1

        return matrix

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
                n_box_min=spell.min_po,
                with_ldv=spell.has_ldv,
            )
        else:
            self.create_mask_range(
                item_value=MapItemList.MASK_SPELL,
                box_x=player.box_x,
                box_y=player.box_y,
                n_box_max=max_po,
                n_box_min=spell.min_po,
                with_ldv=spell.has_ldv,
            )

    # __________________________________________________________________________________________________________________
    def get_positions_in_range(self, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 1):
        positions = []
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
                    if box_content is None:                         # check is in map
                        skip = True
                    elif box_content[self.item_block_index] == 1:  # check is block
                        skip = True
                    elif box_content[self.item_void_index] == 1:    # check is void
                        skip = True

                    # -- do not create mask in MIN PO
                    if abs(y - box_y) + abs(x - box_x) < n_box_min:
                        skip = True

                    if not skip:
                        positions.append((x, y))

                    x += 1

            if y >= box_y:
                n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row += 1  # increase number of boxes by row

            y += 1

        return positions

    # __________________________________________________________________________________________________________________
    def create_mask_range(self, item_value: int, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 1, with_ldv=False):
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

        positions = self.get_positions_in_range(box_x, box_y, n_box_max=n_box_max, n_box_min=n_box_min)

        for position in positions:
            x = position[0]
            y = position[1]

            # -- check if in ldv
            if with_ldv and not self.is_in_ldv(box_x, box_y, box_target_x=x, box_target_y=y):
                continue

            self.matrix[y, x, item_index] = 1

    # __________________________________________________________________________________________________________________
    def create_mask_line(self, item_value: int, box_x: int, box_y: int, n_box_max: int, n_box_min: int = 0, with_ldv: bool = False):
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
                    # -- block, void or outside the map
                    box_content = self.box_content(x, y)
                    if box_content is None:  # check is in map
                        skip = True
                    elif box_content[self.item_block_index] == 1:  # check is block
                        skip = True
                    elif box_content[self.item_void_index] == 1:  # check is void
                        skip = True

                    # -- do not create mask in MIN PO
                    if abs(y - box_y) + abs(x - box_x) < n_box_min:
                        skip = True

                    # -- check if in ldv
                    if not self.is_in_ldv(box_x, box_y, box_target_x=x, box_target_y=y):
                        skip = True

                    if not skip:
                        self.matrix[y, x, item_index] = 1

                    x += 1

            if y == box_y - 1:
                n_box_row = n_box_max  # decrease number of boxes by row if row is above half number of rows
            else:
                n_box_row = 0  # increase number of boxes by row

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
        if not (self.BOX_WIDTH > box_x >= 0 and self.BOX_HEIGHT > box_y >= 0):
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
    def is_in_ldv(self, box_x, box_y, box_target_x, box_target_y):
        distanceX = abs(box_target_x - box_x)
        distanceY = abs(box_target_y - box_y)
        cumulX = box_x
        cumulY = box_y
        cumulN = -1 + distanceX + distanceY
        xInc = 1 if box_target_x > box_x else -1
        yInc = 1 if box_target_y > box_y else -1
        error = distanceX - distanceY
        distanceX *= 2
        distanceY *= 2

        if error > 0:
            cumulX += xInc
            error -= distanceY
        elif error < 0:
            cumulY += yInc
            error += distanceX
        else:
            cumulX += xInc
            error -= distanceY
            cumulY += yInc
            error += distanceX
            cumulN -= 1

        while cumulN > 0:
            if self.BOX_HEIGHT > cumulY >= 0 and self.BOX_WIDTH > cumulX >= 0:
                if self.matrix[cumulY][cumulX][self.item_empty_index] != 1 \
                        and self.matrix[cumulY][cumulX][self.item_void_index] != 1:
                    return False

            if error > 0:
                cumulX += xInc
                error -= distanceY
            elif error < 0:
                cumulY += yInc
                error += distanceX
            else:
                cumulX += xInc
                error -= distanceY
                cumulY += yInc
                error += distanceX
                cumulN -= 1
            cumulN -= 1

        return True

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
    # GET RANDOM INIT POSITION
    def get_random_position(self):
        """ get box_x, box_y of a random empty box """
        positions = self.get_item_positions(MapItemList.EMPTY)
        rand_index = np.random.choice(np.arange(len(positions)))
        return positions[rand_index]

    # __________________________________________________________________________________________________________________
    def get_random_position_in_range(self, box_x, box_y, range_max, rang_min):
        """ get position in range of requested box """
        positions = self.get_positions_in_range(box_x=box_x, box_y=box_y, n_box_max=range_max, n_box_min=rang_min)
        if (box_x, box_y) in positions:
            positions.remove((box_x, box_y))

        return positions[np.random.randint(0, len(positions))]

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
        new_map = np.zeros((h, w, len(item_values)))

        for i in range(len(map)):
            row = map[i]
            for j in range(len(row)):
                item_value = row[j]
                index_item = item_values.index(item_value)
                new_map[i, j, index_item] = 1

        return new_map

    # __________________________________________________________________________________________________________________
    def create_random_map(self, width, height, void_prob=0, blocs_prob=0, item_values=[]):
        if len(item_values) == 0:
            item_values = MapItemList.get_item_values()

        self.BOX_WIDTH = width
        self.BOX_HEIGHT = height

        index_empty = item_values.index(MapItemList.EMPTY)

        index_void = item_values.index(MapItemList.VOID)
        void_array = np.zeros(len(item_values))
        void_array[index_void] = 1

        index_block = item_values.index(MapItemList.BLOCK)
        block_array = np.zeros(len(item_values))
        block_array[index_block] = 1

        # create empty map with void around
        matrix = np.zeros((width, height, len(item_values)))
        matrix[:, :, index_empty] = 1
        matrix[0, :] = void_array
        matrix[-1, :] = void_array
        matrix[:, 0] = void_array
        matrix[:, -1] = void_array

        if void_prob > 0 or blocs_prob > 0:
            for y in range(1, height-1):
                for x in range(1, width-1):
                    prob = random.random()
                    if prob <= void_prob:
                        matrix[y, x] = void_array
                    elif prob <= void_prob + blocs_prob:
                        matrix[y, x] = block_array

        self.matrix = matrix

    # __________________________________________________________________________________________________________________
    @property
    def WIDTH(self):
        return self.BOX_WIDTH * self.BOX_DIM

    @property
    def HEIGHT(self):
        return self.BOX_HEIGHT * self.BOX_DIM
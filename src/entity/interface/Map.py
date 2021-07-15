from entity.interface.MapItemList import MapItemList
from tkinter import Label
import pdb
import numpy as np


class Map:
    BOX_DIM = 50

    def __init__(self):
        self.matrix:        np.ndarray = np.empty(0)

        self.BOX_WIDTH:     int = 0
        self.BOX_HEIGHT:    int = 0
        self.WIDTH:         int = 0
        self.HEIGHT:        int = 0

        self.create()

    def create(self):
        self.matrix = np.asarray([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ], dtype=np.int32)

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
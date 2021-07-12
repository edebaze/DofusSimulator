from tkinter import *
import pdb


BOX_DIM = 50
NUM_BOX_WIDTH = 15
NUM_BOX_HEIGHT = 15
MAP_WIDTH = BOX_DIM * NUM_BOX_WIDTH
MAP_HEIGHT = BOX_DIM * NUM_BOX_HEIGHT

INFOBAR_WIDTH = NUM_BOX_WIDTH
INFOBAR_HEIGHT = 200

CANVAS_WIDTH = MAP_WIDTH
CANVAS_HEIGHT = MAP_HEIGHT + INFOBAR_HEIGHT

root = Tk()
can = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')


def get_selected_box(event):
    """
        get coordinates of selected box
    :param event:
    :return:
    """
    x = event.x // BOX_DIM
    y = event.y // BOX_DIM

    return x, y


def create_circle(x, y, r, coul='red'):                     # pour le dessin des pions
    "tracé d'un cercle de centre (x,y) et de rayon r"
    return can.create_oval(x - r, y - r, x + r, y + r, fill=coul)
from tkinter import *
from entity.interface import Map, InfoBar
import colorama
import pdb

# CONST
SLEEP_TIME = 0.2

# GLOBAL VARS
MAP = Map()
INFO_BAR = InfoBar(MAP)
colorama.init()

RENDER_MODE_ACTIVE = False
root = Tk()
canvas = Canvas(root, width=MAP.WIDTH, height=MAP.HEIGHT+INFO_BAR.HEIGHT, bg='white')


def end_game():
    # TODO : GUI
    # player = None
    # for player in self.players:
    #     if not player.is_dead:
    #         break

    popup = Toplevel()
    popup.title('game over')

    text = f"GAME OVER !"
    end_label = Label(popup, text=text, bg="black", fg="white", width=20, height=10)
    end_label.config(font=("Courier", 32, "italic"))
    end_label.pack()

    Button(popup, text='Quitter', command=root.destroy).pack(padx=10, pady=10)
from tkinter import *
from entity.interface import Map, InfoBar
import pdb

MAP = Map()
INFO_BAR = InfoBar(MAP)

RENDER_MODE_ACTIVE = False
PLAYERS: list = []
CURRENT_PLAYER = None
root = Tk()
canvas = Canvas(root, width=MAP.WIDTH, height=MAP.HEIGHT+INFO_BAR.HEIGHT, bg='white')


def end_game():
    player = None
    for player in PLAYERS:
        if not player.is_dead:
            break

    popup = Toplevel()
    popup.title('game over')

    text = f"GAME OVER ! \n PLAYER {player.index} WON"
    end_label = Label(popup, text=text, bg="black", fg="white", width=20, height=10)
    end_label.config(font=("Courier", 32, "italic"))
    end_label.pack()

    Button(popup, text='Quitter', command=root.destroy).pack(padx=10, pady=10)
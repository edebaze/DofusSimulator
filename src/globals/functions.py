from globals import BOX_DIM, root
from tkinter import *


def get_selected_box(event):
    """
        get coordinates of selected box
    :param event:
    :return:
    """
    x = event.x // BOX_DIM
    y = event.y // BOX_DIM

    return x, y


def end_game(players):
    player = None
    for player in players:
        if not player.is_dead:
            break

    popup = Toplevel()
    popup.title('game over')

    text = f"GAME OVER ! \n PLAYER {player.index} WON"
    end_label = Label(popup, text=text, bg="black", fg="white", width=20, height=10)
    end_label.config(font=("Courier", 32, "italic"))
    end_label.pack()

    Button(popup, text='Quitter', command=root.destroy).pack(padx=10, pady=10)

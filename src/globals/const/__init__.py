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

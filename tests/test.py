from tkinter import *
from PIL import Image, ImageTk
import pdb
from time import sleep
import copy

BOX_DIM = 50


def move(event):
    global a

    x = 0
    for i in range(10):
        x += BOX_DIM

        a.place(x=x)
        frame.update()
        sleep(0.1)


if __name__ == '__main__':
    root = Tk()
    canvas = Canvas(root, width=600, height=500, bg="white")
    canvas.place(x=0, y=0, anchor=NW)

    frame = Frame(root, width=600, height=500)
    frame.pack()

    a_img = ImageTk.PhotoImage(Image.open('../images/class/iop.png').resize((BOX_DIM, BOX_DIM)))
    a = Label(frame, image=a_img)
    a.place(x=0, y=0, anchor=NW)

    b_img = ImageTk.PhotoImage(Image.open('../images/class/cra.jpeg').resize((BOX_DIM, BOX_DIM)))
    b = Label(root, image=b_img)
    b.place(x=0, y=50, anchor=NW)

    root.bind('<space>', move)

    root.mainloop()
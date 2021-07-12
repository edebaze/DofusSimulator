from tkinter import *
from PIL import Image, ImageTk

BOX_DIM = 50

root = Tk()
can = Canvas(root, width=500, height=500, bg="white")
can.place(x=0, y=0, anchor=NW)

box_x = 5
box_y = 5
n_box = 3
color = 'green'
mask = LabelFrame(root, width=(2*n_box+1)*BOX_DIM, height=(2*n_box+1)*BOX_DIM)

y = (n_box - n_box) * BOX_DIM

n_box_row = 0       # number of boxes to create on the current row
for i in range(2*n_box + 1):
    x = (n_box - n_box_row) * BOX_DIM

    for j in range(2*n_box_row + 1):
        skip = False
        # -- do not create mask on the player
        if i == n_box and j == n_box_row:
            skip = True

        if not skip:
            rect = Label(mask, bg=color, padx=BOX_DIM//2, height=0, relief='solid')
            rect.config(font=("Courrier", 0))
            rect.place(x=x, y=y, anchor=NW)

        x += BOX_DIM

    if i >= n_box:
        n_box_row -= 1  # decrease number of boxes by row if row is above half number of rows
    else:
        n_box_row += 1  # increase number of boxes by row

    y += BOX_DIM

# mask.place(x=(box_x - n_box) * BOX_DIM, y=(box_y - n_box_row) * BOX_DIM, anchor=NW)
mask.place(x=0, y=0, anchor=NW)

root.mainloop()
from tkinter import *
from PIL import Image, ImageTk

root = Tk()
can = Canvas(root, width=500, height=500, bg="white")
can.pack()

tk_img = ImageTk.PhotoImage(Image.open('../images/iop.png').resize((50, 50)))
img = can.create_image(100, 50, anchor=NW, image=tk_img)


def move_left(event):
    print('left')
    can.move(img, -10, 0)


def hello(event):
    print('Hello')


root.bind('<Left>', move_left)
root.bind('<Right>', move_left)
root.bind('<Up>', move_left)
root.bind('<Down>', move_left)
root.bind('<space>', hello)


root.mainloop()
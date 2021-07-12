from globals import *
from entity.classes.Class import Class
from entity.spells import Spell
from PIL import Image, ImageTk


class InfoBar:
    PORTRAIT_DIM = 100
    X_PORTRAIT = 100
    Y_PORTRAIT = MAP_HEIGHT + 50

    X_HP = X_PORTRAIT + PORTRAIT_DIM  + 30
    Y_HP = MAP_HEIGHT + 50
    X_PA = X_HP
    Y_PA = Y_HP + 30
    X_PM = X_HP
    Y_PM = Y_PA + 30

    SPELL_IMG_DIM = 40
    NUM_SPELL_IMG_BY_ROW = 8
    NUM_SPELL_ROWS = 8
    X_IMG_MIN = X_PM + 150
    Y_IMG_MIN = MAP_HEIGHT + 50
    X_IMG_MAX = X_IMG_MIN + NUM_SPELL_IMG_BY_ROW * SPELL_IMG_DIM
    Y_IMG_MAX = Y_IMG_MIN + NUM_SPELL_ROWS * SPELL_IMG_DIM

    def __init__(self):
        self.tk_portrait_img: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(Class.IMG_DIR + '/none.png').resize((InfoBar.PORTRAIT_DIM, InfoBar.PORTRAIT_DIM)))
        self.portrait_label = Label(root, image=self.tk_portrait_img)
        self.portrait_label.place(x=InfoBar.X_PORTRAIT, y=InfoBar.Y_PORTRAIT, anchor=NW)

        self.hp_label = Label(root, text="HP : 0 ", bg="white", fg="red")
        self.hp_label.config(font=("Courier", 16, "italic"))
        self.hp_label.place(x=InfoBar.X_HP, y=InfoBar.Y_HP)

        self.pa_label = Label(root, text="PA : 0 ", bg="white", fg="blue")
        self.pa_label.config(font=("Courier", 16, "italic"))
        self.pa_label.place(x=InfoBar.X_PA, y=InfoBar.Y_PA)

        self.pm_label = Label(root, text="PM : 0", bg="white", fg="green")
        self.pm_label.config(font=("Courier", 16, "italic"))
        self.pm_label.place(x=InfoBar.X_PM, y=InfoBar.Y_PM)

        self.tk_spells_imgs: list = []
        self.spells_labels: list = []

    def set_portrait(self, image):
        self.tk_portrait_img = ImageTk.PhotoImage(Image.open(image).resize((InfoBar.PORTRAIT_DIM, InfoBar.PORTRAIT_DIM)))
        self.portrait_label.config(image=self.tk_portrait_img)
        self.portrait_label.image = self.tk_portrait_img

    def set_hp(self, value):
        self.hp_label.config(text='HP : ' + str(value))

    def set_pa(self, value):
        self.pa_label.config(text='PA : ' + str(value))

    def set_pm(self, value):
        self.pm_label.config(text='PM : ' + str(value))

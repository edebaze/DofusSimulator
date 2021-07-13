from tkinter import Label, NW
from entity.classes.Class import Class
from PIL import Image, ImageTk


class InfoBar:
    HEIGHT = 200

    def __init__(self, MAP):
        self.PORTRAIT_DIM = 100
        self.X_PORTRAIT = 30
        self.Y_PORTRAIT = MAP.HEIGHT + 50

        self.X_HP = self.X_PORTRAIT + self.PORTRAIT_DIM + 30
        self.Y_HP = MAP.HEIGHT + 50
        self.X_PA = self.X_HP
        self.Y_PA = self.Y_HP + 30
        self.X_PM = self.X_HP
        self.Y_PM = self.Y_PA + 30

        self.SPELL_IMG_DIM = 40
        self.NUM_SPELL_IMG_BY_ROW = 8
        self.NUM_SPELL_ROWS = 8
        self.X_IMG_MIN = self.X_PM + 150
        self.Y_IMG_MIN = MAP.HEIGHT + 50
        self.X_IMG_MAX = self.X_IMG_MIN + self.NUM_SPELL_IMG_BY_ROW * self.SPELL_IMG_DIM
        self.Y_IMG_MAX = self.Y_IMG_MIN + self.NUM_SPELL_ROWS * self.SPELL_IMG_DIM

        self.tk_portrait_img: (None, ImageTk.PhotoImage) = None
        self.portrait_label = None
        self.hp_label = None
        self.pa_label = None
        self.pm_label = None

        self.tk_spells_imgs: list = []
        self.spells_labels: list = []

# ======================================================================================================================
    def init_labels(self, canvas):
        self.tk_portrait_img = ImageTk.PhotoImage(Image.open(Class.IMG_DIR + '/none.png').resize((self.PORTRAIT_DIM, self.PORTRAIT_DIM)))
        self.portrait_label = Label(canvas, image=self.tk_portrait_img)
        self.portrait_label.place(x=self.X_PORTRAIT, y=self.Y_PORTRAIT, anchor=NW)

        self.hp_label = Label(canvas, text="HP : 0 ", bg="white", fg="red")
        self.hp_label.config(font=("Courier", 16, "italic"))
        self.hp_label.place(x=self.X_HP, y=self.Y_HP)

        self.pa_label = Label(canvas, text="PA : 0 ", bg="white", fg="blue")
        self.pa_label.config(font=("Courier", 16, "italic"))
        self.pa_label.place(x=self.X_PA, y=self.Y_PA)

        self.pm_label = Label(canvas, text="PM : 0", bg="white", fg="green")
        self.pm_label.config(font=("Courier", 16, "italic"))
        self.pm_label.place(x=self.X_PM, y=self.Y_PM)

        self.tk_spells_imgs: list = []
        self.spells_labels: list = []

    def set_portrait(self, image):
        self.tk_portrait_img = ImageTk.PhotoImage(Image.open(image).resize((self.PORTRAIT_DIM, self.PORTRAIT_DIM)))
        self.portrait_label.config(image=self.tk_portrait_img)
        self.portrait_label.image = self.tk_portrait_img

    def set_hp(self, value):
        self.hp_label.config(text='HP : ' + str(value))

    def set_pa(self, value):
        self.pa_label.config(text='PA : ' + str(value))

    def set_pm(self, value):
        self.pm_label.config(text='PM : ' + str(value))

from globals.path import *
from game.spells import SpellList, Spell


class Class:
    IMG_DIR = IMAGE_DIR.replace('\\', '/') + '/class'

    def __init__(self, name):
        self.name: str = name               # name of the class
        self.img_path: str = ''             # path to the class image
        self.spells: list = [SpellList.get(SpellList.OS), SpellList.get(SpellList.CAC)]     # common Spells

    def add_spells(self, spells: (list, int)):
        """
            add spells to the class
        :param spells:
        :return:
        """
        if isinstance(spells, int):
            spells = [spells]

        for spell in spells:
            if spell in self.spells:
                print('Multiple addition of spell', spell)
                continue

            self.spells.append(SpellList.get(spell))
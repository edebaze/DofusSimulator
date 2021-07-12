from entity.spells import SpellList, Spell


class Class:
    IMG_DIR = '../images/class'

    def __init__(self, name):
        self.name: str = name
        self.img_path: str = ''
        self.spells: list = [SpellList.get(SpellList.CAC)]

    def add_spells(self, spells: (list, int)):
        if isinstance(spells, int):
            spells = [spells]

        for spell in spells:
            if spell in self.spells:
                print('Multiple addition of spell', spell)
                continue

            self.spells.append(SpellList.get(spell))
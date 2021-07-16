import random


class Spell:
    IMG_DIR = '../images/spells'

    def __init__(self):
        self.name: str = ''
        self.type: int = 0
        self.img: str = ''

        self.pa: int = 0
        self.po: int = 1
        self.max_damage: int = 0
        self.min_damage: int = 0

        self.is_po_mutable: bool = True

    def damages(self) -> int:
        # return random.randint(self.min_damage, self.max_damage)
        return self.max_damage
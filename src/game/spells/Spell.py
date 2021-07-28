from globals.path import IMAGE_DIR

import numpy as np
import random


class Spell:
    IMG_DIR = IMAGE_DIR.replace('\\', '/') + '/spells'

    ELEMENT_NEUTRAL = 'neutral'
    ELEMENT_FIRE = 'fire'
    ELEMENT_AIR = 'air'
    ELEMENT_WATER = 'water'
    ELEMENT_EARTH = 'earth'
    ELEMENT_BUMP = 'bump'

    ZONE_NONE = 0
    ZONE_ITEM = 1
    ZONE_CENTER = 2

    def __init__(self):
        self.name: str = ''
        self.id: int = 0
        self.img: str = ''

        # PA/PO
        self.pa: int = 0
        self.cooldown: int = 0
        self.min_po: int = 0
        self.max_po: int = 1
        self.is_po_mutable: bool = True
        self.has_ldv: bool = True

        # DAMAGES
        self.elem: str = self.ELEMENT_NEUTRAL
        self.max_damage: int = 0
        self.min_damage: int = 0

        # EFFECTS
        self.pa_retreat: int = 0
        self.pm_retreat: int = 0
        self.po_retreat: int = 0
        self.bump: int = 0

        # SPELL TARGET
        self.is_line: bool = False
        self.spell_target: np.ndarray = np.asarray([[2]])

    def damages(self) -> int:
        # return random.randint(self.min_damage, self.max_damage)
        return self.max_damage

    @staticmethod
    def create_zone(range):
        zone = np.empty(0)
        return zone

    @staticmethod
    def create_zone_cross(range):
        zone = np.empty(0)
        return zone

    @staticmethod
    def create_zone_line(range):
        zone = np.ones((1, range)) * Spell.ZONE_ITEM
        zone[0, range-1] = Spell.ZONE_CENTER
        return zone
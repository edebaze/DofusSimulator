from globals.path import IMAGE_DIR
from game.spells.SpellDirectionList import SpellDirectionList

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
    ZONE_RANGE = 1
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
        self.zone: np.ndarray = np.asarray([[self.ZONE_CENTER]])

    def damages(self) -> int:
        """ damages of spell """
        # return random.randint(self.min_damage, self.max_damage)
        return self.max_damage

    def is_in_zone(self, player, zone_center_x: int, zone_center_y: int):
        """
            check if Player is in spell zone
        :param player:  targeted player
        :param zone_center_x:   box_x of the center of the spell
        :param zone_center_y:   box-y of the center of the spell
        :return:
            (bool) is_in_zone : is player in the zone of the spell
            (bool) dist: distance from center of the zone
        """

        direction = SpellDirectionList.get_direction(box_x=zone_center_x, box_y=zone_center_y, box_x_player=player.box_x, box_y_player=player.box_y)
        zone = SpellDirectionList.orientate_spell(self.zone, direction)

        zone_center = np.argwhere(zone == self.ZONE_CENTER)
        zone_ranges = np.argwhere(zone == self.ZONE_RANGE)
        zone_ranges = np.concatenate([zone_ranges, zone_center])

        for zone_range in zone_ranges:
            zone_range -= zone_center[0]
            if player.box_x == zone_center_x + zone_range[0] and player.box_y == zone_center_y + zone_range[0]:
                dist = abs(zone_range[0]) + abs(zone_range[1])
                return True, dist

        return False, 0

    def get_max_range(self) -> (None, int):
        """ return max range of the spell (for map.get_spell_state()) """
        if not self.is_po_mutable:
            return self.max_po

        return None

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
        zone = np.ones((1, range)) * Spell.ZONE_RANGE
        zone[0, range-1] = Spell.ZONE_CENTER
        return zone
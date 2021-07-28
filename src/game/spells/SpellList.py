from game.spells import Spell

import numpy as np


class SpellList:
    # COMMON SPELLS
    OS = 0
    CAC = 1

    # IOP SPELLS
    PRESSION = 101
    TEMPETE_DE_PUISSANCE = 102
    MARTEAU_DE_MOON = 103

    # CRA SPELLS
    FLECHE_MAGIQUE = 201
    FLECHE_ENFLAMMEE = 202
    FLECHE_GLACEE = 203
    FLECHE_DE_RECULE = 204

    @staticmethod
    def get(spell_id) -> (None, Spell):
        # ===================================================================
        # CLASSIC SPELLS ====================================================
        if spell_id == SpellList.OS:
            spell = Spell()
            spell.name = 'os'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/os.jpeg'
            spell.pa = 0
            spell.max_po = 100
            spell.max_damage = 99999
            spell.min_damage = 99999
            spell.is_po_mutable = True

        elif spell_id == SpellList.CAC:
            spell = Spell()
            spell.name = 'cac'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/cac.jpg'
            spell.pa = 4
            spell.min_po = 1
            spell.max_po = 1
            spell.max_damage = 35
            spell.min_damage = 25
            spell.is_po_mutable = False

        # ===============================================================
        # IOP SPELLS ====================================================
        elif spell_id == SpellList.PRESSION:
            spell = Spell()
            spell.name = 'pression'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/pression.jpeg'
            spell.pa = 3
            spell.min_po = 1
            spell.max_po = 3
            spell.max_damage = 15
            spell.min_damage = 10
            spell.is_po_mutable = False

        elif spell_id == SpellList.TEMPETE_DE_PUISSANCE:
            spell = Spell()
            spell.name = 'tempête de puissance'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/tempete_de_puissance.png'
            spell.pa = 3
            spell.min_po = 3
            spell.max_po = 4
            spell.max_damage = 10
            spell.min_damage = 10
            spell.is_po_mutable = False

        elif spell_id == SpellList.MARTEAU_DE_MOON:
            spell = Spell()
            spell.name = 'marteau de moon'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/marteau_de_moon.jpeg'
            spell.pa = 5
            spell.min_po = 6
            spell.max_po = 6
            spell.max_damage = 20
            spell.min_damage = 10

        # ===============================================================
        # CRA SPELLS ====================================================
        elif spell_id == SpellList.FLECHE_MAGIQUE:
            spell = Spell()
            spell.name = 'fleche magique'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/fleche_magique.jpg'
            spell.pa = 4
            spell.max_po = 7
            spell.elem = Spell.ELEMENT_FIRE
            spell.max_damage = 8
            spell.min_damage = 1

        elif spell_id == SpellList.FLECHE_ENFLAMMEE:
            spell = Spell()
            spell.name = 'fleche enflammée'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/fleche_enflammee.jpg'
            spell.pa = 4
            spell.max_po = 7
            spell.elem = Spell.ELEMENT_FIRE
            spell.max_damage = 20
            spell.min_damage = 1
            spell.bump = 1
            spell.is_line = True
            spell.spell_target = Spell.create_zone_line(4)

        elif spell_id == SpellList.FLECHE_GLACEE:
            spell = Spell()
            spell.name = 'fleche glacée'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/fleche_glacee.jpg'
            spell.pa = 3
            spell.max_po = 7
            spell.elem = Spell.ELEMENT_FIRE
            spell.max_damage = 3
            spell.min_damage = 1
            spell.pa_retreat = 1

        elif spell_id == SpellList.FLECHE_DE_RECULE:
            spell = Spell()
            spell.name = 'fleche de recule'
            spell.id = spell_id
            spell.img = Spell.IMG_DIR + '/fleche_de_recule.jpg'
            spell.pa = 4
            spell.min_po = 2
            spell.max_po = 5
            spell.elem = Spell.ELEMENT_AIR
            spell.max_damage = 10
            spell.min_damage = 1
            spell.bump = 4
            spell.is_line = True

        else:
            print('Unknown spell', spell_id)
            return

        return spell
from game.spells import Spell


class SpellList:
    OS = 0
    CAC = 1
    PRESSION = 2
    FLECHE_MAGIQUE = 3

    @staticmethod
    def get(spell_type) -> (None, Spell):
        if spell_type == SpellList.OS:
            spell = Spell()
            spell.name = 'os'
            spell.type = spell_type
            spell.img = Spell.IMG_DIR + '/os.jpeg'
            spell.pa = 0
            spell.po = 100
            spell.max_damage = 99999
            spell.min_damage = 99999
            spell.is_po_mutable = True

        elif spell_type == SpellList.CAC:
            spell = Spell()
            spell.name = 'cac'
            spell.type = spell_type
            spell.img = Spell.IMG_DIR + '/cac.jpg'
            spell.pa = 4
            spell.po = 1
            spell.max_damage = 35
            spell.min_damage = 25
            spell.is_po_mutable = False

        elif spell_type == SpellList.PRESSION:
            spell = Spell()
            spell.name = 'pression'
            spell.type = spell_type
            spell.img = Spell.IMG_DIR + '/pression.jpeg'
            spell.pa = 3
            spell.po = 3
            spell.max_damage = 13
            spell.min_damage = 10
            spell.is_po_mutable = False

        elif spell_type == SpellList.FLECHE_MAGIQUE:
            spell = Spell()
            spell.name = 'fleche magique'
            spell.type = spell_type
            spell.img = Spell.IMG_DIR + '/fleche_magique.jpg'
            spell.pa = 4
            spell.po = 7
            spell.max_damage = 6
            spell.min_damage = 0

        else:
            print('Unknown spell', spell_type)
            return

        return spell
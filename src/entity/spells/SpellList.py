from entity.spells import Spell


class SpellList:
    CAC = 1
    PRESSION = 2
    FLECHE_MAGIQUE = 3

    @staticmethod
    def get(spell_type) -> (None, Spell):
        if spell_type == SpellList.CAC:
            spell = Spell()
            spell.name = 'cac'
            spell.type = spell_type
            spell.img = Spell.IMG_DIR + '/cac.jpg'
            spell.pa = 4
            spell.po = 1
            spell.max_damage = 20
            spell.min_damage = 18
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
            spell.name = 'fleche_magique'
            spell.type = spell_type
            spell.img = Spell.IMG_DIR + '/fleche_magique.jpg'
            spell.pa = 4
            spell.po = 7
            spell.max_damage = 15
            spell.min_damage = 12

        else:
            print('Unknown spell', spell_type)
            return

        return spell
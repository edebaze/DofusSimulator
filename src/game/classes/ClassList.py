from game.classes.Class import Class
from game.spells import SpellList


class ClassList:
    IOP = 'iop'
    CRA = 'cra'

    @staticmethod
    def get(class_name) -> (None, Class):
        if class_name == ClassList.IOP:
            class_ = Class(class_name)
            class_.img_path = Class.IMG_DIR + '/iop.png'
            class_.add_spells([
                SpellList.PRESSION,
                SpellList.TEMPETE_DE_PUISSANCE,
                SpellList.MARTEAU_DE_MOON,
            ])

        elif class_name == ClassList.CRA:
            class_ = Class(class_name)
            class_.img_path = Class.IMG_DIR + '/cra.jpeg'
            class_.add_spells([
                SpellList.FLECHE_MAGIQUE,
                SpellList.FLECHE_ENFLAMMEE,
                SpellList.FLECHE_DE_RECULE,
            ])

        else:
            print('Error, unknown class', class_name)
            return None

        return class_
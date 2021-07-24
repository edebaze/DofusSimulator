import numpy as np
import copy


class SpellDirectionList:
    CENTER  = 0
    RIGHT   = 1
    LEFT    = 2
    UP      = 3
    DOWN    = 4

    @staticmethod
    def get_direction(box_x: int, box_y: int, box_x_player: int, box_y_player: int) -> int:
        if box_x > box_x_player:
            direction = SpellDirectionList.RIGHT
        elif box_x < box_x_player:
            direction = SpellDirectionList.LEFT
        elif box_y > box_y_player:
            direction = SpellDirectionList.DOWN
        elif box_y < box_y_player:
            direction = SpellDirectionList.UP

        else:
            direction = SpellDirectionList.CENTER

        return direction

    @staticmethod
    def orientate_spell(spell_matrix: np.ndarray, direction: int) -> np.ndarray:
        spell_matrix = copy.copy(spell_matrix)

        if len(spell_matrix.shape) != 2:
            print('BAD SPELL MATRIX')
            print(spell_matrix)
            return spell_matrix

        if direction == SpellDirectionList.CENTER or direction == SpellDirectionList.UP:
            return spell_matrix

        elif direction == SpellDirectionList.RIGHT:
            return spell_matrix.T

        elif direction == SpellDirectionList.LEFT:
            return spell_matrix.T[:, ::-1]

        elif direction == SpellDirectionList.DOWN:
            return spell_matrix[::-1]

        else:
           print('Unkown direction', direction)

        return spell_matrix

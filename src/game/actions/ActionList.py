import inspect


class ActionList:
    END_TURN: int       = 0
    MOVE_LEFT: int      = 1
    MOVE_RIGHT: int     = 2
    MOVE_UP: int        = 3
    MOVE_DOWN: int      = 4
    CAST_SPELL_1: int   = 5
    CAST_SPELL_2: int   = 6
    CAST_SPELL_3: int   = 7
    CAST_SPELL_4: int   = 8

    @staticmethod
    def get_actions():
        actions = [action_value for (action_name, action_value) in inspect.getmembers(ActionList) if ActionList.is_action_name(action_name)]
        actions.sort()
        return actions

    @staticmethod
    def is_action_name(action_name: str) -> bool:
        if not action_name.isupper():
            return False

        if action_name.startswith('_'):
            return False

        return True

    @staticmethod
    def get_cast_spell(spell_index: int):
        action_name = 'CAST_SPELL_' + str(spell_index)
        actions = [value for (name, value) in inspect.getmembers(ActionList) if action_name == name]
        if len(actions) == 0:
            print('Unable to find action', action_name)

        return actions[0]

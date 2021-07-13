import inspect


class ActionList:
    END_TURN: int       = 0
    MOVE_LEFT: int      = 1
    MOVE_RIGHT: int     = 2
    MOVE_UP: int        = 3
    MOVE_DOWN: int      = 4
    CAST_SPELL: int     = 5

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
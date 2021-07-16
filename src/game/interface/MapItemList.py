import inspect

class MapItemList:
    EMPTY:      int = 0
    VOID:       int = 1
    BLOCK:      int = 2

    PLAYER_1:   int = 5
    PLAYER_2:   int = 6

    @staticmethod
    def get_player_value(player_index: int) -> (None, int):
        var_name = 'PLAYER_' + str(player_index + 1)
        values = [value for (name, value) in inspect.getmembers(MapItemList) if name == var_name]

        if len(values) == 0:
            print('Unable to find item_value of', var_name)
            return None
        if len(values) > 1:
            print('Too many item_value for', var_name)
            print(values)
            return None

        return values[0]


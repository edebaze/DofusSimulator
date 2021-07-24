import inspect


class MapItemList:
    EMPTY:          int = 0
    VOID:           int = 1
    BLOCK:          int = 2

    PLAYER_1:       int = 100
    PLAYER_2:       int = 101

    MASK_PM:       int = 1000
    MASK_SPELL:    int = 1001

    MAP_BOX:    list = [EMPTY, VOID, BLOCK]
    PLAYERS:    list = [PLAYER_1, PLAYER_2]
    MASKS:      list = [MASK_PM, MASK_SPELL]

    @staticmethod
    def get_item_values():
        item_values = [item_value for (item_name, item_value) in inspect.getmembers(MapItemList) if MapItemList.is_item_name(item_name) and isinstance(item_value, int)]
        item_values.sort()
        return item_values

    @staticmethod
    def is_item_name(item_name: str) -> bool:
        if not item_name.isupper():
            return False

        if item_name.startswith('_'):
            return False

        return True

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


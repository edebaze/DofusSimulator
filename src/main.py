from entity.GameController import GameController


if __name__ == '__main__':
    game_controller = GameController()
    state, reward, done = game_controller.reset()
    game_controller.render()

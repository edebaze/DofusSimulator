from entity.GameController import GameController
from agents import Agent


if __name__ == '__main__':
    game_controller = GameController([None, None])
    state = game_controller.reset()
    game_controller.render()

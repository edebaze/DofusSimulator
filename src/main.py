from entity.GameController import GameController
from agents import Agent


if __name__ == '__main__':
    game_controller = GameController([None, Agent()])
    state, reward, done = game_controller.reset()
    game_controller.render()

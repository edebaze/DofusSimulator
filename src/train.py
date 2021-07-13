from entity.GameController import GameController


if __name__ == '__main__':
    env = GameController()
    state, reward, done = env.reset()

from entity.GameController import GameController
from agents import Agent
import pdb

NUM_GAMES = 100
MAX_TURN_GAME = 100

if __name__ == '__main__':
    env = GameController([None, None])
    actions = env.actions
    states = []
    scores = []
    dones = []

    for i in range(NUM_GAMES):
        print('========================================================')
        print('GAME :', i)
        state, score, done = env.reset()

        j = 0
        while not done and j < MAX_TURN_GAME:
            continue_playing = True
            while continue_playing:
                action = Agent.choose_random_action(actions)
                states.append(state)
                state, reward, action, continue_playing = env.step(action)

                score += reward
                scores.append(score)
                dones.append(done)

            j += 1

    pdb.set_trace()


from game.Engine import Engine
from game.GUI import GUI
from agents import Agent, NewAgent

import tensorflow as tf
import numpy as np

NUM_GAMES = 50000
MODULO_WATCH = 200

MAP_NUMBER = 1

if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()

    env = Engine(MAP_NUMBER)
    state = env.reset()

    agent1 = NewAgent(
        is_activated=True,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        n_actions=env.n_actions,
        actions=env.actions,
    )

    agent2 = Agent(
        is_activated=True,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
    )

    env = Engine(MAP_NUMBER, [agent1, agent2])

    scores_1 = []
    scores_2 = []
    for i in range(NUM_GAMES):
        score_1, score_2 = env.play_game()

        scores_1.append(score_1)
        scores_2.append(score_2)
        avg_score_1 = np.mean(scores_1[-100:])
        avg_score_2 = np.mean(scores_2[-100:])

        print('episode:', i, '| P1 score ', score_1, '| avg_score %.2f' % avg_score_1, '|| P2 score %.2f' % score_2, '| avg_score %.2f' % avg_score_2)

        if i % MODULO_WATCH == 0 and i != 0:
            gui = GUI(env)
            gui.reset()
            gui.render()

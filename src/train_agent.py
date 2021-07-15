from entity.Engine import Engine
from agents import Agent

import pdb
import colorama

import tensorflow as tf
import time
import numpy as np


NUM_GAMES = 50

LR = 1e-3
EPOCHS = 50
BATCH_SIZE = 128


if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()
    env = Engine([None, None])
    state = env.reset()
    n_actions = env.n_actions

    agent = Agent(
        lr=LR,
        input_dim=state.shape,
        actions=env.actions,
    )
    scores = []
    eps_history = []

    start = time.time()

    for i in range(NUM_GAMES):
        done = False
        score = 0
        state = env.reset()

        while not done:
            continue_playing = True
            while continue_playing and not done:
                action = agent.choose_action(state)
                new_state, reward, done, continue_playing = env.step(action)

                # TODO : REMOVE LATER (keep only data for player 1)
                if env.turn % 2 == 0:
                    agent.store_transition(
                        state=state,
                        action=action,
                        reward=reward,
                        new_state=new_state,
                        done=done
                    )

                    score += reward
                    agent.learn()
                # TODO ======================================

                state = new_state
            # END TURN -----------------------------------------------

        eps_history.append(agent.epsilon)
        scores.append(score)
        avg_score = np.mean(scores[-100:])

        print('episode:', i, '| score ', score, '| avg_score %.2f' % avg_score, '| epsilon %.2f' % agent.epsilon)

    end = time.time()

    print(NUM_GAMES, 'games done in %.2f seconds' % (end-start))
    pdb.set_trace()


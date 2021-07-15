from entity.GameController import GameController, CURRENT_PLAYER
from agents import Agent

import pdb
import colorama

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import numpy as np


NUM_GAMES = 1

LR = 1e-3
EPOCHS = 50
BATCH_SIZE = 128


if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()
    env = GameController([None, None])
    state = env.reset()
    n_actions = env.n_actions

    agent = Agent(
        lr=LR,
        input_dim=state.shape,
        actions=env.actions,
    )
    scores = []
    eps_history = []

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

        if score > 1000:
            pdb.set_trace()

        print('episode:', i, '| score ', score, '| avg_score %.2f' % avg_score, '| epsilon %.2f' % agent.epsilon)

    pdb.set_trace()


from entity.Engine import Engine
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


INIT_NUM_GAMES = 30
MAX_TURN_GAME = 100
MAX_ACTION_IN_TURN = 10

LR = 1e-3
EPOCHS = 50
BATCH_SIZE = 128


def create_training_data(num_games: int, min_score: int, model: (None, Model) = None):
    states = np.empty(0)
    actions = np.empty(0)
    rewards = np.empty(0)

    for i in range(num_games):
        states_ = []
        actions_ = []
        rewards_ = []

        done = False
        score = 0
        state = env.reset()

        j = 0
        while not done and j < MAX_TURN_GAME:
            print('============================================================================')
            print('TURN:', j)

            continue_playing = True
            while continue_playing:
                if model is None:
                    action = Agent.choose_random_action(env.actions)
                else:
                    pred_actions = model.predict(np.asarray([state], dtype=np.int32))
                    action_arg = np.argmax(pred_actions)
                    action = env.actions[action_arg]

                new_state, reward, done, continue_playing = env.step(action)

                # TODO : REMOVE LATER (keep only data for player 1)
                if j % 2 == 0 and reward >= 0:
                    states_.append(state)
                    actions_.append(action)
                    rewards_.append(reward)
                    score += reward
                # TODO ======================================

                state = new_state
            # END TURN -----------------------------------------------

            j += 1

        # KEEP : only game with a min score
        if score > min_score:
            if len(states) == 0:
                states = np.asarray(states_, dtype=np.int32)
            else:
                states = np.concatenate([states, np.asarray(states_, dtype=np.int32)])
            actions = np.concatenate([actions, np.asarray(actions_, dtype=np.int32)])

        # END GAME ---------------------------------------------------
    # END LOOP ALL GAMES ---------------------------------------------

    colorama.init()
    print(colorama.Fore.RESET)

    if len(actions) == 0:
        pdb.set_trace()
        return states, actions

    # TODO : remove [:, -n_actions:]
    return states, to_categorical(actions)[:, -n_actions:]


def create_model(input_dim) -> Model:
    """
        Create prediction model
    """
    inputs = Input(input_dim)
    x = Dense(64, activation='relu')(inputs)
    x = Dense(128, activation='relu')(x)

    # Output Layer
    outputs = Dense(n_actions, activation='softmax')(x)

    model = Model(inputs, outputs, name="Classic Model")

    model.compile(
        loss='categorical_crossentropy',
        optimizer=Adam(learning_rate=LR),
        metrics=['accuracy']
    )

    return model


def train_model(model, training_data, training_labels):
    model.fit(
        training_data, training_labels,
        epochs=EPOCHS,
        verbose=1,
        batch_size=BATCH_SIZE
    )

    return model


if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()

    env = Engine([None, None])
    n_actions = env.n_actions

    # -- FIRST TRAINING
    X, Y = create_training_data(INIT_NUM_GAMES, 0)

    model = create_model(X[0].shape)
    model = train_model(model, X, Y)

    # -- TRAINING WITH MODEL DECISION
    X, Y = create_training_data(num_games=INIT_NUM_GAMES, min_score=200, model=model)
    model = train_model(model, X, Y)

    X, Y = create_training_data(num_games=INIT_NUM_GAMES, min_score=300, model=model)
    model = train_model(model, X, Y)

    X, Y = create_training_data(num_games=INIT_NUM_GAMES, min_score=400, model=model)
    model = train_model(model, X, Y)

    pdb.set_trace()


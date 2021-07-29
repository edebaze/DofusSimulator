import os
import sys
import inspect

dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
while dir_path.split('\\')[-1] != 'src':
    dir_path = os.path.dirname(dir_path)
sys.path.insert(0, dir_path)

from globals import *

from game import Engine
from game import Player
from game.interface.GUI import GUI
from game.classes import ClassList
from game.actions.ActionList import ActionList
from agents import Agent
from agents.pnj_agents import Poutch

import tensorflow as tf
from tensorflow import keras

import pandas as pd
import numpy as np
import random


"""
    TRAINING SCRIPT : train the agent to optimize his damages against a Poutch on a block/void free map
"""

NUM_GAMES = 500000
MODULO_TRAIN = 10  # train bot each N games
MODULO_WATCH = 500  # watch bots on GUI each N games
MODULO_SAVE = 200  # save models each N games

MAP_NUMBER = 1

CNN_STRUCTURE = [
    {'type': 'CNN', 'size': 128, 'kernel_size': 2, 'strides': 1, 'padding': 'valid'},
    {'type': 'CNN', 'size': 128, 'kernel_size': 2, 'strides': 1, 'padding': 'valid'},
    {'type': 'MaxPool', 'pool_size': 2},
    {'type': 'CNN', 'size': 256, 'kernel_size': 2, 'strides': 1, 'padding': 'valid'},
    {'type': 'CNN', 'size': 256, 'kernel_size': 2, 'strides': 1, 'padding': 'same'},
    {'type': 'MaxPool', 'pool_size': 2},
]

FC_MODEL_STRUCTURE = [
    {'type': 'FC', 'size': 32},
    {'type': 'FC', 'size': 32},
]

OUTPUT_BLOCK_STRUCTURE = [
    {'type': 'FC', 'size': 512},
    {'type': 'FC', 'size': 512},
    {'type': 'FC', 'size': 256},
    {'type': 'FC', 'size': 256},
]

if __name__ == '__main__':
    # ==================================================================================================================
    # INITIALISATION
    # ==================================================================================================================
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.compat.v1.Session(config=config)
    tf.compat.v1.keras.backend.set_session(session)

    actions = ActionList.get_actions()
    last_loss = 0
    last_loss2 = 0
    turns = []
    scores = []
    scores_2 = []

    model_iop = keras.models.load_model(os.path.join(MODEL_DIR, 'saved', 'iop_1.h5'))
    model_cra = keras.models.load_model(os.path.join(MODEL_DIR, 'saved', 'cra_1.h5'))

    # -- create agent 1
    agent1 = Agent(
        is_activated=True,
        cnn_model_structure=CNN_STRUCTURE,
        fc_model_structure=FC_MODEL_STRUCTURE,
        output_block_structure=OUTPUT_BLOCK_STRUCTURE,
        # model=model_iop,
    )

    # ==================================================================================================================
    # MAIN LOOP
    # ==================================================================================================================
    for i in range(NUM_GAMES):
        # ==============================================================================================================
        # RESET ENV
        player = Player(class_name=ClassList.IOP, team=1, agent=agent1, BASE_HP=150, BASE_PM=4)
        poutch = Player(
            class_name=ClassList.CRA,
            team=2,
            agent=Poutch(),
            BASE_HP=random.randint(200, 1000),
            BASE_PA=random.randint(1, 12),
            BASE_PM=random.randint(1, 6),
            BASE_PO=random.randint(1, 6),
        )
        env = Engine(MAP_NUMBER, [player, poutch])

        # -- randomly place player and poutch
        player.box_x, player.box_y = env.map.get_random_empty_position()
        box_x, box_y = env.map.get_random_empty_position()
        while box_x == player.box_x and box_y == player.box_y:
            box_x, box_y = env.map.get_random_empty_position()
        poutch.box_x, poutch.box_y = box_x, box_y

        # ==============================================================================================================
        # GENERATE DATA
        score, _ = env.play_game()

        turns.append(env.turn)
        scores.append(score)
        avg_turn = np.mean(turns[-100:])
        avg_score = np.mean(scores[-100:])

        print('episode:', i, 'turns:', env.turn, 'avg_turns: %.2f' % avg_turn, '| P1 score ', score, '| avg_score %.2f' % avg_score)

        # ==============================================================================================================
        # TRAIN MODELS
        if i % MODULO_TRAIN == 0 and i != 0:
            # -- train model on the memory
            loss = agent1.train_on_memory()
            # -- set loss display to red if loss is increasing and to green if loss is decreasing
            color = colorama.Fore.RED if last_loss < loss else colorama.Fore.GREEN
            last_loss = loss

            # -- apply changes to epsilon on agents
            agent1.apply_epsilon_decay()

            # -- display result of the training to the console
            print('P1 loss:', color, '%.2f' % loss, colorama.Fore.RESET, '| epsilon %.2f' % agent1.epsilon)
            print('==============================================================================================================')

        # ==============================================================================================================
        # SAVE MODELS
        if i % MODULO_SAVE == 0 and i != 0:
            # if os.path.isfile(MODEL_EXCEL_FILE):
            #     excel_content = pd.read_excel(MODEL_EXCEL_FILE)
            # else:
            #     excel_content = pd.DataFrame()

            for player in env.players:
                agent = player.agent
                agent.save_model()

                # # SAVE EXCEL
                # data = dict()

                # # -- score
                # data['model_filename'] = agent.model_filename
                # data['score'] = score if player.index == 0 else score_2
                # data['avg_score'] = avg_score if player.index == 0 else avg_score_2
                # data['epsilon'] = agent1.epsilon if player.index == 0 else agent2.epsilon

                # # -- env
                # data['turn'] = env.turn
                # data['actions'] = str(env.actions)

                # df = pd.Series(data)
                # excel_content = pd.concat([excel_content, df.T])

            # excel_content.to_excel(MODEL_EXCEL_FILE)

        # ==============================================================================================================
        # SHOW GAMES
        if i % MODULO_WATCH == 0 and i != 0:
            gui = GUI(env)
            gui.reset()
            gui.render()

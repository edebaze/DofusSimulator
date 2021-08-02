from globals import *

from game import Engine
from game import Player
from game.interface.GUI import GUI
from game.classes import ClassList
from agents import Agent

import tensorflow as tf
from tensorflow import keras

import pandas as pd
import numpy as np

NUM_GAMES = 500000
MODULO_TRAIN = 10           # train bot each N games
MODULO_WATCH = 500          # watch bots on GUI each N games
MODULO_SAVE = 200           # save models each N games

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

    last_loss1 = 0
    last_loss2 = 0
    turns = []
    scores_1 = []
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

    # -- create agent 2
    agent2 = Agent(
        is_activated=True,
        cnn_model_structure=CNN_STRUCTURE,
        fc_model_structure=FC_MODEL_STRUCTURE,
        output_block_structure=OUTPUT_BLOCK_STRUCTURE,
        # model=model_cra
    )

    # ==================================================================================================================
    # MAIN LOOP
    # ==================================================================================================================
    for i in range(NUM_GAMES):
        # ==============================================================================================================
        # RESET ENV
        player_1 = Player(class_name=ClassList.IOP, team=1, agent=agent1, BASE_HP=50, BASE_PM=4)
        player_2 = Player(class_name=ClassList.CRA, team=2, agent=agent2, BASE_HP=50, BASE_PM=3)
        env = Engine(MAP_NUMBER, [player_1, player_2])

        # ==============================================================================================================
        # GENERATE DATA
        score_1, score_2 = env.play_game()

        turns.append(env.turn)
        scores_1.append(score_1)
        scores_2.append(score_2)
        avg_turn = np.mean(turns[-100:])
        avg_score_1 = np.mean(scores_1[-100:])
        avg_score_2 = np.mean(scores_2[-100:])

        print('episode:', i, 'turns:', env.turn, 'avg_turns: %.2f' % avg_turn, '| P1 score ', score_1, '| avg_score %.2f' % avg_score_1, '|| P2 score %.2f' % score_2, '| avg_score %.2f' % avg_score_2)

        # ==============================================================================================================
        # TRAIN MODELS
        if i % MODULO_TRAIN == 0 and i != 0:
            # -- train model on the memory
            loss1 = agent1.train_on_memory()
            loss2 = agent2.train_on_memory()
            # -- set loss display to red if loss is increasing and to green if loss is decreasing
            color1 = colorama.Fore.RED if last_loss1 < loss1 else colorama.Fore.GREEN
            color2 = colorama.Fore.RED if last_loss2 < loss2 else colorama.Fore.GREEN
            last_loss1 = loss1
            last_loss2 = loss2
            
            # -- apply changes to epsilon on agents
            agent1.apply_epsilon_decay()
            agent2.apply_epsilon_decay()

            # -- display result of the training to the console  
            print('P1 loss:', color1, '%.2f' % loss1, colorama.Fore.RESET, '| epsilon %.2f' % agent1.epsilon) 
            print('P2 loss:', color2, '%.2f' % loss2, colorama.Fore.RESET, '| epsilon %.2f' % agent2.epsilon)
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
                # data['score'] = score_1 if player.index == 0 else score_2
                # data['avg_score'] = avg_score_1 if player.index == 0 else avg_score_2
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

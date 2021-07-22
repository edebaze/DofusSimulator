from globals import *

from game.Engine import Engine
from game.interface.GUI import GUI
from agents import Agent

import pandas as pd
import numpy as np

NUM_GAMES = 500000
MODULO_WATCH = 500
MODULO_SAVE = 50
NUM_SHOW_GAMES = 0

MAP_NUMBER = 1

if __name__ == '__main__':
    # ==================================================================================================================
    # INITIALISATION
    # ==================================================================================================================
    env = Engine(MAP_NUMBER)
    state = env.reset()

    # model_dir = ''
    model_dir = '../models/1626798305425235100/'

    agent1 = Agent(
        is_activated=True,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
        model_file=model_dir + 'player_1.h5',
    )

    agent2 = Agent(
        is_activated=True,
        model_structure=[256, 128],
        input_dim=state.shape,
        actions=env.actions,
        model_file=model_dir + 'player_2.h5',
    )

    if model_dir is not None:
        agent1.load_model()
        agent2.load_model()

    env = Engine(MAP_NUMBER, [agent1, agent2])

    scores_1 = []
    scores_2 = []

    # ==================================================================================================================
    # INIT BOTS DATA WITH USER MOVES
    # ==================================================================================================================
    env.reset()
    env.players[0].agent.is_activated = False       # set to False to take control
    for k in range(NUM_SHOW_GAMES):
        gui = GUI(env)
        gui.reset()
        gui.render()

    env.players[0].agent.is_activated = True        # set to True to set agent in auto mode

    # ==================================================================================================================
    # MAIN LOOP
    # ==================================================================================================================
    for i in range(NUM_GAMES):
        # ==============================================================================================================
        # PLAY GAMES
        score_1, score_2, epsilon_1, epsilon_2 = env.play_game()

        scores_1.append(score_1)
        scores_2.append(score_2)
        avg_score_1 = np.mean(scores_1[-100:])
        avg_score_2 = np.mean(scores_2[-100:])

        print('episode:', i, 'turns:', env.turn, '| P1 score ', score_1, '| avg_score %.2f' % avg_score_1, '| epsilon %.2f' % epsilon_1, '|| P2 score %.2f' % score_2, '| avg_score %.2f' % avg_score_2, '| epsilon %.2f' % epsilon_2)


        if i % 10 == 0 and i != 0:
            agent1.train_on_memory() 
            agent2.train_on_memory()
        # ==============================================================================================================
        # SAVE MODELS
        if i % MODULO_SAVE and i != 0:
            if os.path.isfile(MODEL_EXCEL_FILE):
                excel_content = pd.read_excel(MODEL_EXCEL_FILE)
            else:
                excel_content = pd.DataFrame()

            for player in env.players:
                agent = player.agent
                agent.save_model()

                # SAVE EXCEL
                data = dict()

                # -- score
                data['model_file'] = agent.model_file
                data['score'] = score_1 if player.index == 0 else score_2
                data['avg_score'] = avg_score_1 if player.index == 0 else avg_score_2
                data['epsilon'] = epsilon_1 if player.index == 0 else epsilon_2

                # -- env
                data['turn'] = env.turn
                data['actions'] = str(env.actions)

                df = pd.Series(data)
                excel_content = pd.concat([excel_content, df.T])

            # excel_content.to_excel(MODEL_EXCEL_FILE)

        # ==============================================================================================================
        # SHOW GAMES
        if i % MODULO_WATCH == 0 and i != 0:
            gui = GUI(env)
            gui.reset()
            gui.render()

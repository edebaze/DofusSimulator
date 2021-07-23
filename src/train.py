from globals import *

from game.Engine import Engine
from game.interface.GUI import GUI
from agents import Agent

import pandas as pd
import numpy as np

NUM_GAMES = 500000
MODULO_TRAIN = 10           # train bot each N games
MODULO_WATCH = 500          # watch bots on GUI each N games
MODULO_SAVE = 200           # save models each N games
NUM_SHOW_GAMES = 0          # number of games to play (by the user) before training to start generating training data

MAP_NUMBER = 1

if __name__ == '__main__':
    # ==================================================================================================================
    # INITIALISATION
    # ==================================================================================================================
    env = Engine(MAP_NUMBER)
    state = env.reset()

    agent1 = Agent(
        is_activated=True,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
    )

    agent2 = Agent(
        is_activated=True,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
    )

    env = Engine(MAP_NUMBER, [agent1, agent2])

    last_loss1 = 0
    last_loss2 = 0
    turns = []
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

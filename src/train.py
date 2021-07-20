from globals import *

from game.Engine import Engine
from game.interface.GUI import GUI
from agents import Agent

import pandas as pd
import numpy as np

NUM_GAMES = 500000
MODULO_WATCH = 500000
MODULO_SAVE = 500

MAP_NUMBER = 1

if __name__ == '__main__':
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

    scores_1 = []
    scores_2 = []
    for i in range(NUM_GAMES):
        score_1, score_2, epsilon_1, epsilon_2 = env.play_game()

        scores_1.append(score_1)
        scores_2.append(score_2)
        avg_score_1 = np.mean(scores_1[-100:])
        avg_score_2 = np.mean(scores_2[-100:])

        print('episode:', i, 'turns:', env.turn, '| P1 score ', score_1, '| avg_score %.2f' % avg_score_1, '| epsilon %.2f' % epsilon_1, '|| P2 score %.2f' % score_2, '| avg_score %.2f' % avg_score_2, '| epsilon %.2f' % epsilon_2)

        if i % MODULO_SAVE:
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

        if i % MODULO_WATCH == 0 and i != 0:
            gui = GUI(env)
            gui.reset()
            gui.render()

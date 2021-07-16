from game.Engine import Engine
from game.GUI import GUI
from agents import Agent, NewAgent

import tensorflow as tf
import numpy as np

MAP_NUMBER = 1

if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()

    env = Engine(map_number=MAP_NUMBER)
    state = env.reset()

    # agent1 = NewAgent(
    #     is_activated=False,
    #     model_structure=[512, 512, 256, 256],
    #     input_dim=state.shape,
    #     n_actions=env.n_actions,
    #     actions=env.actions,
    # )

    agent1 = Agent(
        is_activated=False,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
    )

    agent2 = Agent(
        is_activated=True,
        model_structure=[256, 128],
        input_dim=state.shape,
        actions=env.actions,
    )

    env = Engine(map_number=MAP_NUMBER, agents=[agent1, agent2])
    gui = GUI(env)
    gui.reset()
    gui.render()


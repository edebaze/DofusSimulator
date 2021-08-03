from game import Player
from globals.path import *
from game.Engine import Engine
from game.classes import ClassList
from game.interface.GUI import GUI
from agents import Agent
from tensorflow import keras

MAP_NUMBER = 2

if __name__ == '__main__':
    env = Engine(map_number=MAP_NUMBER)
    state = env.reset()

    model_iop = keras.models.load_model(os.path.join(MODEL_DIR, 'saved', 'iop_2.h5'))
    model_cra = keras.models.load_model(os.path.join(MODEL_DIR, 'saved', 'cra_2.h5'))

    agent1 = Agent(
        is_activated=True,
        mem_size=1,
        input_dim=[state[0].shape, state[1].shape],
        actions=env.actions,
        epsilon=0,
        epsilon_end=0,
        model=model_iop,
    )

    agent2 = Agent(
        is_activated=True,
        mem_size=1,
        input_dim=[state[0].shape, state[1].shape],
        actions=env.actions,
        epsilon=0,
        epsilon_end=0,
        model=model_cra,
    )

    player_1 = Player(class_name=ClassList.IOP, team=1, agent=agent1, BASE_HP=50, BASE_PM=4)
    player_2 = Player(class_name=ClassList.CRA, team=2, agent=agent2, BASE_HP=50, BASE_PM=3)

    env = Engine(map_number=MAP_NUMBER, players=[player_1, player_2])
    env.initialize()
    gui = GUI(env)
    gui.reset()
    gui.render()


from game.Engine import Engine
from game.interface.GUI import GUI
from agents import Agent

MAP_NUMBER = 1

if __name__ == '__main__':
    env = Engine(map_number=MAP_NUMBER, flag_create_dir=False)
    state = env.reset()

    agent1 = Agent(
        is_activated=False,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
        mem_size=1
    )

    agent2 = Agent(
        is_activated=False,
        model_structure=[512, 512, 256, 256],
        input_dim=state.shape,
        actions=env.actions,
        mem_size=1
    )

    env = Engine(map_number=MAP_NUMBER, agents=[agent1, agent2])
    gui = GUI(env)
    gui.reset()
    gui.render()


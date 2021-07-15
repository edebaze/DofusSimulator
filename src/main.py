from entity.Engine import Engine
from agents.Agent import Agent
from agents import Agent
import tensorflow as tf

NUM_GAMES = 1

LR = 1e-3
EPOCHS = 50
BATCH_SIZE = 128

if __name__ == '__main__':
    tf.compat.v1.disable_eager_execution()
    env = Engine([None, None])
    state = env.reset()

    agent1 = Agent(
        lr=LR,
        input_dim=state.shape,
        actions=env.actions,
    )

    agent2 = Agent(
        lr=LR,
        input_dim=state.shape,
        actions=env.actions,
    )

    game_controller = Engine([agent1, agent2])
    game_controller.reset()
    game_controller.render()

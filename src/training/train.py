import os
import sys
import inspect

dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
while dir_path.split('\\')[-1] != 'src':
    dir_path = os.path.dirname(dir_path)
sys.path.insert(0, dir_path)

from training.Trainer import Trainer
from agents.Agent import Agent
from game.classes import ClassList


if __name__ == '__main__':
    agent = Agent(
        mem_size=1e6,
        gamma=0.99,
        epsilon_decay=0.99,
        epochs=5,
        batch_size=1024,
        lr=1e-4,
        cnn_model_structure=Trainer.CNN_STRUCTURE,
        fc_model_structure=Trainer.FC_MODEL_STRUCTURE,
        output_block_structure=Trainer.OUTPUT_BLOCK_STRUCTURE,
    )

    trainer = Trainer()
    trainer.train(agent=agent, class_name=ClassList.IOP)
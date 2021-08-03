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


CNN_STRUCTURE = [
        {'type': 'CNN', 'size': 64, 'kernel_size': (3, 3), 'strides': 1, 'padding': 'same'},
        {'type': 'CNN', 'size': 64, 'kernel_size': (3, 3), 'strides': 1, 'padding': 'same'},
        {'type': 'MaxPool', 'pool_size': 2},
        {'type': 'CNN', 'size': 128, 'kernel_size': (3, 3), 'strides': 1, 'padding': 'same'},
        {'type': 'CNN', 'size': 128, 'kernel_size': (3, 3), 'strides': 1, 'padding': 'same'},
        {'type': 'MaxPool', 'pool_size': 2},
        {'type': 'CNN', 'size': 256, 'kernel_size': (3, 3), 'strides': 1, 'padding': 'same'},
        {'type': 'CNN', 'size': 256, 'kernel_size': (3, 3), 'strides': 1, 'padding': 'same'},
        {'type': 'MaxPool', 'pool_size': 2},
    ]

FC_MODEL_STRUCTURE = [
    {'type': 'FC', 'size': 64},
    {'type': 'FC', 'size': 32},
]

OUTPUT_BLOCK_STRUCTURE = [
    {'type': 'FC', 'size': 256},
    {'type': 'FC', 'size': 256},
    {'type': 'FC', 'size': 128},
    {'type': 'FC', 'size': 128},
]


if __name__ == '__main__':
    agent = Agent(
        is_activated=True,
        mem_size=1e6,
        gamma=0.95,
        epsilon_decay=0.99,
        batch_size=4096,
        epochs=5,
        lr=1e-4,
        cnn_model_structure=CNN_STRUCTURE,
        fc_model_structure=FC_MODEL_STRUCTURE,
        output_block_structure=OUTPUT_BLOCK_STRUCTURE,
    )

    trainer = Trainer()
    trainer.train(agent=agent, class_name=ClassList.IOP)

from globals.path import *
from training.Dataset import Dataset
from game.Engine import Engine
from game.classes import ClassList
from game.spells import SpellList
from agents.Agent import Agent

import tensorflow as tf
import numpy as np
import importlib


class Trainer:
    CNN_STRUCTURE = [
        {'type': 'CNN', 'size': 64, 'kernel_size': (2, 2), 'strides': 1, 'padding': 'valid'},
        {'type': 'CNN', 'size': 64, 'kernel_size': (2, 2), 'strides': 1, 'padding': 'valid'},
        {'type': 'MaxPool', 'pool_size': 2},
        {'type': 'CNN', 'size': 128, 'kernel_size': (2, 2), 'strides': 1, 'padding': 'valid'},
        {'type': 'CNN', 'size': 128, 'kernel_size': (2, 2), 'strides': 1, 'padding': 'same'},
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

    def __init__(self) -> None:
        self.training_modules: dict = {
            'poutch': {
                'poutch_01': 5000,
            }
        }

        self.batch_size = 128
        self.lr = 3e-4
        self.optimizer = tf.optimizers.Adam(learning_rate=self.lr)
        self.loss_fn = tf.keras.losses.MeanSquaredError()
        self.training_data = None

    def train(self, agent: (None, Agent) = None, class_name: str = ''):
        if agent is None:
            agent = self.create_agent()

        class_ = ClassList.get(class_name)
        if class_ is None:
            print('Error : unknown class', class_name)
            return

        for module, n_games in self.training_modules.items():
            if module == 'spells':
                for sub_module, n_games in n_games.items():
                    for spell in class_.spells[2:]:
                        module += '.' + sub_module
                        self.train_on_module(agent, spell=spell, class_name=class_name, module=module, n_games=n_games)

            elif module == 'poutch':
                for sub_module, n_games in n_games.items():
                    module += '.' + sub_module
                    self.train_on_module(agent, class_name=class_name, module=module, n_games=n_games)

    def train_on_module(self, agent: Agent, module: str, **kwargs):
        """
            train agent on a specific training module
        :param agent:       agent to train
        :param module:      module of training
        :param spell:       specific spell to train on
        :param class_name:  name of the class of the Agent
        :param n_games:     number of game on the training
        :return:
        """
        module = self.load_training_module(module)
        module.train(agent=agent, **kwargs)

    def learning_rate_scheduler(self):
        return self.lr

    def create_agent(self):
        return Agent(
            is_activated=True,
            mem_size=1e6,
            gamma=0.999,
            epsilon_decay=0.99,
            epochs=5,
            batch_size=self.batch_size,
            lr=self.lr,
            cnn_model_structure=Trainer.CNN_STRUCTURE,
            fc_model_structure=Trainer.FC_MODEL_STRUCTURE,
            output_block_structure=Trainer.OUTPUT_BLOCK_STRUCTURE,
        )

    @staticmethod
    def load_training_module(module_path):
        training_dir = TRAINING_DIR.split('\\')[-1]

        if training_dir not in module_path:
            module_path = training_dir + '.' + module_path
        return importlib.import_module(module_path)

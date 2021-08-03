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
    def __init__(self) -> None:
        self.training_modules: dict = {
            'poutch': {
                'poutch_01': 5000,
            }
        }

    def train(self, agent: Agent = None, class_name: str = ''):
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

    @staticmethod
    def load_training_module(module_path):
        training_dir = TRAINING_DIR.split('\\')[-1]

        if training_dir not in module_path:
            module_path = training_dir + '.' + module_path
        return importlib.import_module(module_path)

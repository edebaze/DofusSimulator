import os
import sys
import inspect

dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
while dir_path.split('\\')[-1] != 'src':
    dir_path = os.path.dirname(dir_path)
sys.path.insert(0, dir_path)

from globals import *

from game import Engine
from game import Player
from game.interface.GUI import GUI
from game.classes import ClassList
from game.spells import SpellList, Spell
from game.actions.ActionList import ActionList
from agents import Agent
from agents.pnj_agents import Poutch

import tensorflow as tf
from tensorflow import keras

import pandas as pd
import numpy as np
import random
import copy


"""
    TRAINING SCRIPT : train the agent to use a spell against a poutch
    
    ENV : 
        - map_size : (7 x 7)
        - accepted_actions : [END_TURN, CAST_SPELL_(requested_spell), MOVE]
    
    PARAMETERS : 
        - agent : agent to train
        - class_name : Class to train (cf: ClassList)
        - spell : Spell to train the agent on (cf SpellList)
        - min_pm : number of pm the player must walk to be in range
        - max_pm : max pm the player must walk to be in range
"""

NUM_GAMES = 500000
MODULO_TRAIN = 10  # train bot each N games
MODULO_WATCH = 500  # watch bots on GUI each N games
MODULO_SAVE = 200  # save models each N games

MAP_NUMBER = 1

CLASS_TO_TRAIN = ClassList.IOP
SPELL_TO_TRAIN = SpellList.PRESSION

CNN_STRUCTURE = [
    {'type': 'CNN', 'size': 64, 'kernel_size': (2, 2, 1), 'strides': 1, 'padding': 'valid'},
    {'type': 'CNN', 'size': 64, 'kernel_size': (2, 2, 1), 'strides': 1, 'padding': 'valid'},
    {'type': 'MaxPool', 'pool_size': 2},
    {'type': 'CNN', 'size': 128, 'kernel_size': (2, 2, 1), 'strides': 1, 'padding': 'valid'},
    {'type': 'CNN', 'size': 128, 'kernel_size': (2, 2, 1), 'strides': 1, 'padding': 'same'},
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


def train(agent: Agent, spell: Spell, class_name: str, min_pm: int = 0, max_pm: int = 0,
          n_games: int = NUM_GAMES, modulo_train: int = MODULO_TRAIN, modulo_save: int = MODULO_SAVE, modulo_watch: int = MODULO_WATCH):

    """
        Train an agent on a specific spell of a specific class

    :param agent:           agent to train
    :param spell:           spell to train
    :param class_name:      class to train
    :param min_pm:          minimum pm that the player must walk to be in range of the enemy
    :param max_pm:          maximum pm that the player must walk to be in range of the enemy
    :param n_games:         number of games to play
    :param modulo_train:    train each N games
    :param modulo_save:     save model each N games
    :param modulo_watch:    watch game each N games
    :return:
    """
    engine = None
    last_loss = 0
    turns = []
    scores = []

    # -- set blocked actions
    set_blocked_actions(agent=agent, spell=spell, class_name=class_name)

    for i in range(n_games):
        engine = create_engine(agent=agent, spell=spell, class_name=class_name, min_pm=min_pm, max_pm=max_pm)
        score, _ = engine.play_game()

        turns.append(engine.turn)
        scores.append(score)
        avg_turn = np.mean(turns[-100:])
        avg_score = np.mean(scores[-100:])

        print('episode:', i, 'turns:', engine.turn, '| avg_turns: %.2f' % avg_turn, '| P1 score ', score,
              '| avg_score %.2f' % avg_score)

        # ==============================================================================================================
        # TRAIN MODELS
        if i % modulo_train == 0 and i != 0:
            # -- train model on the memory
            loss = agent.train_on_memory()
            # -- set loss display to red if loss is increasing and to green if loss is decreasing
            color = colorama.Fore.RED if last_loss < loss else colorama.Fore.GREEN
            last_loss = loss

            # -- apply changes to epsilon on agents
            agent.apply_epsilon_decay()

            # -- display result of the training to the console
            print('P1 loss:', color, '%.2f' % loss, colorama.Fore.RESET, '| epsilon %.2f' % agent.epsilon)
            print('==============================================================================================================')

        # ==============================================================================================================
        # SAVE MODELS
        if i % modulo_save == 0 and i != 0:
            save(engine)

        # ==============================================================================================================
        # SHOW GAMES
        if i % modulo_watch == 0 and i != 0:
            engine = create_engine(agent=agent, spell=spell, class_name=class_name, min_pm=min_pm, max_pm=max_pm)
            render(engine)

    agent.permanently_blocked_actions = []  # remove perma blocked actions

    return engine


def set_blocked_actions(agent, spell, class_name):
    actions = ActionList.get_actions()
    index_spell = None
    class_ = ClassList.get(class_name)
    for i in range(len(class_.spells)):
        if class_.spells[i].id == spell.id:
            index_spell = i
            break

    if index_spell is None:
        print('Unable to find spell', spell.name)
        return

    action = ActionList.get_cast_spell(index_spell)
    index_action = actions.index(action)

    agent.permanently_blocked_actions = [action for action in actions if action not in [index_action, ActionList.END_TURN]]


def create_engine(agent: Agent, spell: Spell, class_name: str, min_pm: int, max_pm: int):
    player = Player(class_name=class_name, team=1, agent=agent, BASE_HP=150, BASE_PM=4)
    poutch = Player(
        class_name=ClassList.CRA,
        team=2,
        agent=Poutch(),
        BASE_HP=100,
        BASE_PA=random.randint(1, 12),
        BASE_PM=random.randint(1, 6),
        BASE_PO=random.randint(1, 6),
    )
    engine = Engine(MAP_NUMBER, [player, poutch])

    # -- create random map
    engine.map.create_random_map(7, 7)

    # -- randomly place player and poutch
    max_range = spell.max_po  + max_pm
    if spell.is_po_mutable:
        max_range += player.po
    min_range = spell.min_po + min_pm

    player.box_x, player.box_y = engine.map.get_random_position()
    poutch.box_x, poutch.box_y = engine.map.get_random_position_in_range(player.box_x, player.box_y, max_range, min_range)

    engine.initialize()

    return engine


def render(engine):
    gui = GUI(engine)
    gui.reset()
    gui.render()


def save(engine):
    for player in engine.players:
        agent = player.agent
        agent.save_model()


if __name__ == '__main__':
    # ==================================================================================================================
    # INITIALISATION
    # ==================================================================================================================
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.compat.v1.Session(config=config)
    tf.compat.v1.keras.backend.set_session(session)

    # -- create agent 1
    agent = Agent(
        is_activated=True,
        mem_size=1e6,
        gamma=0.999,
        cnn_model_structure=CNN_STRUCTURE,
        fc_model_structure=FC_MODEL_STRUCTURE,
        output_block_structure=OUTPUT_BLOCK_STRUCTURE,
    )

    set_blocked_actions(agent, SPELL_TO_TRAIN, CLASS_TO_TRAIN)

    train(agent, SPELL_TO_TRAIN, CLASS_TO_TRAIN)

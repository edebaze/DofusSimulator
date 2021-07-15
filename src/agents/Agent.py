from agents.ReplayBuffer import ReplayBuffer

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import numpy as np

import pdb


class Agent:
    LR = 1e-3
    BATCH_SIZE = 64

    MEM_SIZE = 1000000          # size of the memory tables
    GAMMA = 0.99                # percentage of the past reward to add to the current reward in the Q-table

    EPSILON = 1                 # percentage of chances to take a random action
    EPSILON_DECAY = 0.999       # decrease of epsilon at each predictions
    EPSILON_END = 1e-2          # min value of epsilon
    EPSILON_RESET = 20000       # reset epsilon each n predictions
    EPSILON_RESET_VALUE = 0.2   # value of espilon when epsilon is reset

    def __init__(self, actions, input_dim, batch_size=BATCH_SIZE, gamma=GAMMA, epsilon=EPSILON, epsilon_decay=EPSILON_DECAY,
                 epsilon_end=EPSILON_END, epsilon_reset=EPSILON_RESET, epsilon_reset_value=EPSILON_RESET_VALUE, lr=LR, mem_size=MEM_SIZE,
                 model_file='model.h5'):

        self.memory = ReplayBuffer(mem_size=mem_size, input_dim=input_dim)

        self.actions = actions
        self.n_actions = len(actions)  # number of actions

        self.lr = lr  # learning rate
        self.gamma = gamma  # percentage of the past reward to add to the current reward in the Q-table
        self.epsilon = epsilon  # percentage of chances to take a random action
        self.epsilon_decay = epsilon_decay  # decrease of epsilon at each predictions
        self.epsilon_end = epsilon_end  # min value of epsilon
        self.epsilon_reset = epsilon_reset  # reset epsilon each n values
        self.epsilon_reset_value = epsilon_reset_value  # value of espilon when epsilon is reset

        self.input_dim = input_dim
        self.batch_size = batch_size

        self.model = self.create_model()

        self.model_file = model_file

    def create_model(self) -> Model:
        """
            Create prediction model
        """
        inputs = Input(self.input_dim)
        x = Dense(128, activation='relu')(inputs)
        x = Dense(256, activation='relu')(x)
        outputs = Dense(self.n_actions, activation=None)(x)

        model = Model(inputs, outputs, name="DQN model")
        model.compile(
            loss='mse',
            optimizer=Adam(learning_rate=self.lr)
        )
        return model

    def store_transition(self, state, action, reward, new_state, done):
        """
            Store state and results at index i
        """
        self.memory.store_transition(state, action, reward, new_state, done)

    def choose_action(self, state, allow_random=True):
        """
            Choose an action from an observation
        """

        # -- check if epsilon need to be reseted
        if allow_random and self.epsilon_reset > 0 and self.memory.mem_cnter % self.epsilon_reset == 0 and self.memory.mem_cnter > 0:
            self.epsilon = self.epsilon_reset_value

        # -- choose random action (if random is allowed)
        if np.random.random() < self.epsilon and allow_random:
            action = np.random.choice(self.actions)

        # -- choose action from model prediction
        else:
            state = np.array([state])
            action = self.model.predict(state)
            action = np.argmax(action)

        return action

    def learn(self):
        """
            Train model
        """
        if self.memory.mem_cnter < self.batch_size:
            return

        states, new_states, actions, rewards, dones = self.memory.sample_buffer(self.batch_size)

        q_eval = self.model.predict(states)  # predicted current Q table
        q_next = self.model.predict(new_states)  # predicted NEXT Q table
        q_target = np.copy(q_eval)  # copy q_eval

        batch_index = np.arange(self.batch_size, dtype=np.int32)

        q_target[batch_index, actions] = rewards + self.gamma * np.max(q_next, axis=1) * dones

        self.model.train_on_batch(states, q_target)

        self.epsilon = self.epsilon * self.epsilon_decay if self.epsilon > self.epsilon_end else self.epsilon_end

    def save_model(self):
        self.model.save(self.model_file)

    def load_model(self):
        self.model = keras.load_model(self.model_file)

    @staticmethod
    def choose_random_action(actions):
        return np.random.choice(actions)
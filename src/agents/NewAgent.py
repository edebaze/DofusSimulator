from agents.NewReplayBuffer import NewReplayBuffer

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import numpy as np

import pdb


class NewAgent:
    LR = 1e-3
    BATCH_SIZE = 64

    MEM_SIZE = 1000000          # size of the memory tables
    GAMMA = 0.99                # percentage of the past reward to add to the current reward in the Q-table

    EPSILON = 1                 # percentage of chances to take a random action
    EPSILON_DECAY = 0.999       # decrease of epsilon at each predictions
    EPSILON_END = 1e-2          # min value of epsilon
    EPSILON_RESET = 10000       # reset epsilon each n predictions
    EPSILON_RESET_VALUE = 0.2   # value of espilon when epsilon is reset

    def __init__(self, actions, is_activated: bool = True, model_structure: list = [],  n_actions: int = 0, input_dim: tuple = (), model: (Model, None) = None, batch_size=BATCH_SIZE, gamma=GAMMA, epsilon=EPSILON, epsilon_decay=EPSILON_DECAY,
                 epsilon_end=EPSILON_END, epsilon_reset=EPSILON_RESET, epsilon_reset_value=EPSILON_RESET_VALUE, lr=LR, mem_size=MEM_SIZE,
                 model_file='model.h5'):

        self.is_activated: bool = is_activated          # is the agent auto playing or not
        self.memory = NewReplayBuffer(mem_size=mem_size, input_dim=input_dim, n_actions=n_actions)

        self.actions = actions
        self.n_actions = len(actions)  # number of actions

        self.model_structure = model_structure          # structure of the model
        self.lr = lr                                    # learning rate
        self.gamma = gamma                              # percentage of the past reward to add to the current reward in the Q-table
        self.epsilon = epsilon                          # percentage of chances to take a random action
        self.epsilon_decay = epsilon_decay              # decrease of epsilon at each predictions
        self.epsilon_end = epsilon_end                  # min value of epsilon
        self.epsilon_reset = epsilon_reset              # reset epsilon each n values
        self.epsilon_reset_value = epsilon_reset_value  # value of espilon when epsilon is reset

        self.input_dim: tuple = input_dim               # learning rate of the model
        self.batch_size: int = batch_size               # batch size of the model

        self.model: Model = self.create_model() if model is None else model

        self.model_file: str = model_file

    def create_model(self) -> Model:
        """
            Create prediction model
        """
        inputs = Input(self.input_dim)

        x = Dense(self.model_structure[0], activation='relu')(inputs)
        for layer in self.model_structure[1:]:
            x = Dense(layer, activation='relu')(x)

        outputs = Dense(self.n_actions, activation=None)(x)

        model = Model(inputs, outputs, name="DQN model")
        model.compile(
            loss='mse',
            optimizer=Adam(learning_rate=self.lr)
        )
        return model

    def store_transition(self, state, new_state, action, reward, q_table, done):
        """
            Store state and results at index i
        """
        self.memory.store_transition(state=state, action=action, reward=reward, new_state=new_state, q_table=q_table, done=done)

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

        states, new_state, q_table, actions, rewards, terminals = self.memory.sample_buffer(self.batch_size)

        q_next = self.model.predict(new_state)
        q_target = np.copy(q_table)

        batch_index = np.arange(self.batch_size, dtype=np.int32)

        q_target[batch_index, actions] = rewards + self.gamma * np.max(q_next, axis=1) * terminals

        self.model.train_on_batch(states, q_target)

        self.epsilon = self.epsilon * self.epsilon_decay if self.epsilon > self.epsilon_end else self.epsilon_end

    def save_model(self):
        self.model.save(self.model_file)

    def load_model(self):
        self.model = keras.load_model(self.model_file)

    @staticmethod
    def choose_random_action(actions):
        return np.random.choice(actions)
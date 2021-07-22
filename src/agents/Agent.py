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
    EPOCHS = 5
    LR = 3e-4
    BATCH_SIZE = 128

    MEM_SIZE = 1e6  # size of the memory tables
    GAMMA = 0.99  # percentage of the past reward to add to the current reward in the Q-table

    EPSILON = 1  # percentage of chances to take a random action
    EPSILON_DECAY = 0.9  # decrease of epsilon at each predictions
    EPSILON_END = 1e-2  # min value of epsilon
    EPSILON_RESET = 1e6  # reset epsilon each n predictions
    EPSILON_RESET_VALUE = 0.1 # value of espilon when epsilon is reset

    def __init__(
        self,
        actions,
        is_activated: bool = True,
        model_structure: list = [],
        input_dim: tuple = (),
        model: Model = None,
        epochs=EPOCHS,
        lr=LR,
        batch_size=BATCH_SIZE,
        gamma=GAMMA,
        epsilon=EPSILON,
        epsilon_decay=EPSILON_DECAY,
        epsilon_end=EPSILON_END,
        epsilon_reset=EPSILON_RESET,
        epsilon_reset_value=EPSILON_RESET_VALUE,
        mem_size=MEM_SIZE,
        model_filename="model.h5",
    ):

        self.is_activated: bool = is_activated  # is the agent auto playing or not
        self.input_dim: tuple = input_dim       # dimension of the input data
        self.actions = actions                  # array of actions that can be taken
        self.n_actions = len(actions)           # number of actions

        self.memory = ReplayBuffer(mem_size=mem_size, input_dim=self.input_dim, n_actions = self.n_actions)

        # Model description
        self.model_structure = model_structure  # structure of the model
        self.gamma = gamma                      # percentage of the past reward to add to the current reward in the Q-table
        self.epsilon = epsilon                  # percentage of chances to take a random action
        self.epsilon_decay = epsilon_decay      # decrease of epsilon at each predictions
        self.epsilon_end = epsilon_end          # min value of epsilon
        self.epsilon_reset = epsilon_reset      # reset epsilon each n values
        self.epsilon_reset_value = epsilon_reset_value  # value of espilon when epsilon is reset

        # Training hyperparameters
        self.batch_size = batch_size
        self.epoch = epochs
        self.lr = lr
        self.optimizer = tf.optimizers.Adam(learning_rate=self.lr)
        self.loss_fn = tf.keras.losses.MeanSquaredError()

        # Model instanciation
        self.model: Model = self.create_model() if model is None else model

        # Load / Save model
        self.model_filename: str = model_filename

    def create_model(self) -> Model:
        """
        Create prediction model
        """
        inputs = Input(self.input_dim)

        x = Dense(self.model_structure[0], activation="relu")(inputs)
        for layer in self.model_structure[1:]:
            x = Dense(layer, activation="relu")(x)

        outputs = Dense(self.n_actions, activation=None)(x)

        model = Model(inputs, outputs)
        model.compile(loss="mse", optimizer=Adam(learning_rate=self.lr))
        return model

    def store_transition(self, state, action_table, reward, new_state, done):
        """
        Store state and results at index i
        """
        self.memory.store_transition(state, action_table, reward, new_state, done)

    def train_on_memory(self):
        # Declare dataset
        training_dataset = tf.data.Dataset.from_tensor_slices(self.memory.get_buffer())

        training_dataset = training_dataset.repeat(self.epoch).shuffle(self.epoch).batch(
            self.batch_size).prefetch(tf.data.AUTOTUNE)

        # Training loop
        for training_data in training_dataset:
            loss = self.train_step(*training_data)      # train model on batch of data
            loss_array.append(loss)                     # add batch loss to loss array

        return np.mean(loss_array)  # return mean of loss array

    @tf.function
    def train_step(self, current_states, next_states, action_tables, rewards, terminals):
        """
            train on a batch of data

        :param: current_states : states at each step i
        :param: next_states : new states after each action at step i
        :param: action_tables : action taken at each step i (as True/False table)
        :param: rewards : rewards won at each step i after action i
        :param: terminals : is game done at each step (0: game done, 1: game continue)

        :return: loss
        """
        q_current = self.model(current_states)   # Initialize the target q table with the current q table
        q_next = self.model(next_states)         # Predict next q table

        q_target = rewards + self.gamma * tf.reduce_max(q_next, axis=1) * terminals
        q_target = tf.tile(q_target[..., tf.newaxis], (1, self.n_actions))
        q_target = tf.where(action_tables, q_target, q_current)

        with tf.GradientTape() as tape:
            q_current = self.model(current_states)
            loss = self.loss_fn(q_current, q_target)

        grads = tape.gradient(loss, self.model.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.model.trainable_weights))

        return loss

    def apply_epsilon_decay(self) -> None:
        """ apply decay on epsilon or reset of epsilon """
        # -- check if epsilon need to be reseted
        if self.epsilon_reset > 0 \
                and self.memory.mem_cnter % self.epsilon_reset == 0 \
                and self.memory.mem_cnter > 0:

            self.epsilon = self.epsilon_reset_value

        else:
            self.epsilon = max(self.epsilon_end, self.epsilon*self.epsilon_decay)
            
    def choose_action(self, state, allow_random=True):
        """
            Choose an action from a state
        """
        # -- choose random action (if random is allowed)
        if np.random.random() < self.epsilon and allow_random:
            action = np.random.choice(self.actions)

        # -- choose action from model prediction
        else:
            state = np.array([state])
            action = self.model(state)
            action = np.argmax(action)

        return action

    def save_model(self):
        self.model.save(self.model_filename)

    def load_model(self):
        self.model = tf.keras.models.load_model(self.model_filename)

    @staticmethod
    def choose_random_action(actions):
        return np.random.choice(actions)

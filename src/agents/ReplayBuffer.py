import numpy as np
import tensorflow as tf


class ReplayBuffer:
    """
        The ReplayBuffer holds the memory of
            - states      : state of the game at each index
            - new_states  : state of the game at index (i+1) after a taken action
            - actions     : actions taken at each index
            - rewards     : rewards gain at each index for each actions
            - terminals   : game done or not

        Contains all methods to stock and display the memory
    """

    def __init__(self, mem_size, input_dim, n_actions):
        self.mem_size: int = int(mem_size)          # max size of the memory
        self.n_actions: int = n_actions             # number of actions
        self.mem_cnter = 0                          # current index of state

        # Memory of STATES
        self.map_memory = np.zeros((self.mem_size, *input_dim[0]), dtype=np.float)                  # memory of map states
        self.new_map_memory = np.zeros((self.mem_size, *input_dim[0]), dtype=np.float32)              # memory of map states after taken action
        self.players_state_memory = np.zeros((self.mem_size, *input_dim[1]), dtype=np.float)        # memory of players states
        self.new_players_state_memory = np.zeros((self.mem_size, *input_dim[1]), dtype=np.float)    # memory of players states after taken action

        # Memory of results (action, rewards and terminal)
        self.action_table_memory = np.zeros((self.mem_size, self.n_actions), dtype=np.float)        # memory of action taken at state i
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float)                                # memory of rewards of action taken at state i
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.float)                              # BOOL : game done or not at state i

    def update_memory(self, new_state=None, reward=None):
        """ when a player starts his turn : update new_state_memory and reward of last turn """
        if self.mem_cnter == 0:
            return

        index = (self.mem_cnter - 1) % self.mem_size

        if new_state is not None:
            self.new_map_memory[index] = new_state[0]
            self.new_players_state_memory[index] = new_state[1]

        if reward is not None:
            self.reward_memory[index] += reward

    def store_transition(self, state, action_table, reward, new_state, done):
        """
            store state and results at index i
        """
        index = self.mem_cnter % self.mem_size

        self.map_memory[index] = state[0]
        self.new_map_memory[index] = new_state[0]
        self.players_state_memory[index] = state[1]
        self.new_players_state_memory[index] = new_state[1]
        self.action_table_memory[index] = action_table
        self.reward_memory[index] = reward
        self.terminal_memory[index] = 1 - done

        self.mem_cnter += 1

    def get_buffer(self):
        k = min(self.mem_cnter, self.mem_size)

        return (
            tf.cast(self.map_memory[:k], tf.float32),
            tf.cast(self.players_state_memory[:k], tf.float32),
            tf.cast(self.new_map_memory[:k], tf.float32),
            tf.cast(self.new_players_state_memory[:k], tf.float32),
            tf.cast(self.action_table_memory[:k], tf.bool),
            tf.cast(self.reward_memory[:k], tf.float32), 
            tf.cast(self.terminal_memory[:k], tf.float32)
        )
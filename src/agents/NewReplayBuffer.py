import numpy as np


class NewReplayBuffer:
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
        self.mem_size = mem_size        # max size of the memory
        self.mem_cnter = 0              # current index of state

        # Memory of STATES
        self.state_memory = np.zeros((self.mem_size, *input_dim), dtype=np.int32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dim), dtype=np.int32)
        self.q_table_memory = np.zeros((self.mem_size, n_actions), dtype=np.int32)

        # Memory of results (action, rewards and terminal)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)  # memory of action taken at state i
        self.reward_memory = np.zeros(self.mem_size, dtype=np.int32)  # memory of rewards of action taken at state i
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.int32)  # BOOL : game done or not at state i

    def store_transition(self, state, new_state, action, reward, q_table, done):
        """
            store state and results at index i
        """
        index = self.mem_cnter % self.mem_size

        self.state_memory[index] = state
        self.new_state_memory[index] = new_state
        self.action_memory[index] = action
        self.q_table_memory[index] = q_table
        self.reward_memory[index] = reward
        self.terminal_memory[index] = 1 - done

        self.mem_cnter += 1

    def sample_buffer(self, batch_size):
        """
            return values for a batch of data
        """
        max_mem = min(self.mem_cnter, self.mem_size)
        batch = np.random.choice(max_mem, batch_size, replace=False)

        states = self.state_memory[batch]
        new_states = self.new_state_memory[batch]
        q_tables = self.q_table_memory[batch]
        actions = self.action_memory[batch]
        rewards = self.reward_memory[batch]
        terminals = self.terminal_memory[batch]

        return states, new_states, q_tables, actions, rewards, terminals
import tensorflow as tf
import numpy as np

from training.Dataset import Dataset
from game.Engine import Engine
from agents.Agent import Agent


class Trainer:
    def __init__(self) -> None:

    
        self.batch_size = 64
        self.lr = 1e-3
        self.optimizer = tf.optimizers.Adam(learning_rate=self.lr)
        self.loss_fn = tf.keras.losses.MeanSquaredError()
        self.training_data = None

    def learning_rate_scheduler(self):
        return self.lr

    

    def train(self, agent, engine):
        
        MAP_NUMBER = 1
        NUM_GAME = 100


    
        
        engine = Engine(map_number=MAP_NUMBER, agents=[agent1, agent2])
        
        for generation in range(self.num_generation):
            for _ in NUM_GAME:
                engine.play_game()

            



        for model_generation_index in range():
            self.epsilon = self.epsilon * self.epsilon_decay if self.epsilon > self.epsilon_end else self.epsilon_end
            dataset = Dataset()
            for states, new_state, q_table, actions, rewards, terminals in dataset:
                
                loss = self.train_step(states, new_state, q_table, actions, rewards, terminals)



        
        
    



    
    


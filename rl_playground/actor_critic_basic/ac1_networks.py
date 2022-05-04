import os
from pickletools import optimize
from tkinter import S
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense
import gym
from tensorflow.keras.optimizers import Adam
import tensorflow_probability as tfp


# a class that generalises to either of the two networks
class ActorCriticNetwork(tf.keras.Model):

    # constructor for the model
    def __init__(self, n_actions, fc1_dims = 1024, fc2_dims = 512,
        name = 'actor_critic', chkpt_dir = "rl-playground/actor_critic_basic/tmp2/actor_critic"):

        # interface initialise
        super(ActorCriticNetwork, self).__init__()

        # set dimensions for outputs of fully connected layers
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims

        self.n_actions = n_actions
        self.model_name = name

        # this is to save weights so we don't have to train every time
        self.checkpoint_dir = chkpt_dir
        self.checkpoint_file = os.path.join(self.checkpoint_dir, name+'ac')

        # fully connected layers 1 and 2
        self.fc1 = Dense(self.fc1_dims, activation = 'relu')
        self.fc2 = Dense(self.fc2_dims, activation = 'relu')

        # value function output layer -> return a single value
        self.v = Dense(1, activation = None)

        # policy function output layer -> return a distribution over actions
        self.pi = Dense(n_actions, activation = 'softmax')

    
    # feed forward through the layer
    def call(self, state):

        value = self.fc1(state)
        value = self.fc2(value)

        v = self.v(value)
        pi = self.pi(value)

        # compute a value and a policy
        return (v, pi)


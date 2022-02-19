import os
from pickletools import optimize
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Dense
import gym
from tensorflow.keras.optimizers import Adam
import tensorflow_probability as tfp

from ac1_networks import ActorCriticNetwork

class Agent:

    def __init__(self, alpha = 0.0001, gamma = 0.99, n_actions = 2):

        self.alpha = alpha
        self.gamma = gamma
        
        self.n_actions = n_actions
        self.action = None

        self.action_space = [i for i in range(self.n_actions)]
        self.actor_critic = ActorCriticNetwork(n_actions=n_actions)

        self.actor_critic.compile(optimizer = Adam(learning_rate = alpha))


    def choose_action(self, observation):

        state = tf.convert_to_tensor([observation])

        # returns softmaxed probabilities from the network
        _, probs = self.actor_critic(state)

        action_probabilities = tfp.distributions.Categorical(probs=probs)
        action = action_probabilities.sample()

        self.action = action

        return action.numpy()[0]



    def save_models(self):
        print('... saving models ...')
        self.actor_critic.save_weights(self.actor_critic.checkpoint_file)

    def load_models(self):
        print('... loading models ...')
        self.actor_critic.load_weights(self.actor_critic.checkpoint_file)


    # the learning function
    def learn(self, state, reward, state_n, done):

        state = tf.convert_to_tensor([state], dtype = tf.float32)
        state_n = tf.convert_to_tensor([state_n], dtype = tf.float32)
        reward = tf.convert_to_tensor([reward], dtype = tf.float32)
        
        with tf.GradientTape() as tape:

            state_value, probs = self.actor_critic(state)
            state_value_n, _ = self.actor_critic(state_n)

            # cleans up the tensor by getting rid of size 1 dimensions
            state_value = tf.squeeze(state_value)
            state_value_n = tf.squeeze(state_value_n)

            actions_probs = tfp.distributions.Categorical(probs = probs)
            log_prob = actions_probs.log_prob(self.action)

            delta = reward + self.gamma * state_value_n*(1-int(done)) - state_value

            actor_loss = - log_prob * delta
            critic_loss = delta ** 2

            total_loss = actor_loss + critic_loss


        gradient = tape.gradient(total_loss, self.actor_critic.trainable_variables)
        self.actor_critic.optimizer.apply_gradients(zip(
            gradient, self.actor_critic.trainable_variables))

        

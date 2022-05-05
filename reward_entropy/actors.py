import os
from pickletools import optimize
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
import tensorflow_probability as tfp

from networks import ActorCriticNetwork

class Agent:

    def __init__(self, alpha = 0.0001, gamma = 0.99, n_actions = 2):

        self.alpha = alpha      # learning rate
        self.gamma = gamma      # discount factor
        
        self.n_actions = n_actions # number of availible actions
        self.action = None         # the action we choose

        self.action_space = [i for i in range(self.n_actions)]
        self.actor_critic = ActorCriticNetwork(n_actions=n_actions)

        # initialise an optimizer for the agent
        self.actor_critic.compile(optimizer = Adam(learning_rate = alpha))


    def choose_action(self, observation):

        # save the game state as a tensor
        state = tf.convert_to_tensor([observation])

        # returns softmaxed probabilities from the network
        _, probs = self.actor_critic(state)

        action_probabilities = tfp.distributions.Categorical(probs=probs)
        action = action_probabilities.sample()

        # pick an action from the distribution and set it as our move
        self.action = action

        return action.numpy()[0]


    # save weights
    def save_models(self):
        print('... saving models ...')
        self.actor_critic.save_weights(self.actor_critic.checkpoint_file)

    # load weights
    def load_models(self):
        print('... loading models ...')
        self.actor_critic.load_weights(self.actor_critic.checkpoint_file)


    # the training function to learn the parameters
    def learn(self, state, reward, state_new, done):

        # convert all the openai stuff to tensorflow
        state = tf.convert_to_tensor([state], dtype = tf.float32)
        state_new = tf.convert_to_tensor([state_new], dtype = tf.float32)
        reward = tf.convert_to_tensor([reward], dtype = tf.float32)
        
        with tf.GradientTape() as tape:

            # get the action distribution
            state_value, probs = self.actor_critic(state)

            # get the value of moving to a new state
            state_value_new, _ = self.actor_critic(state_new)

            # cleans up the tensor by getting rid of size 1 dimensions
            state_value = tf.squeeze(state_value)
            state_value_new = tf.squeeze(state_value_new)

            actions_probs = tfp.distributions.Categorical(probs = probs)
            log_prob = actions_probs.log_prob(self.action)

            delta = reward + self.gamma * state_value_new*(1-int(done)) - state_value

            # define the loss functions
            actor_loss = - log_prob * delta
            critic_loss = delta ** 2
            total_loss = actor_loss + critic_loss


        # apply the gradient descent algorithm
        gradient = tape.gradient(total_loss, self.actor_critic.trainable_variables)
        self.actor_critic.optimizer.apply_gradients(zip(
            gradient, self.actor_critic.trainable_variables))

        

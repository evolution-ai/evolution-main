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
import time
from ac1_actors import Agent


# helper to plot a learning curve
def plot_learning_curve(x, scores, figure_file):
    running_avg = np.zeros(len(scores))
    for i in range(len(running_avg)):
        running_avg[i] = np.mean(scores[max(0, i-100):(i+1)])
    plt.plot(x, running_avg)
    plt.title('Running average of previous 100 scores')
    plt.savefig(figure_file)


# main method
if __name__ == '__main__':

    # call the open AI gym environment
    env = gym.make('CartPole-v1')

    # create an actor
    agent = Agent(alpha = 1e-5, n_actions=env.action_space.n)
    n_games = 5

    # for file saves only
    filename = 'cartpole.png'
    figure_file = 'plots/' + filename

    # create score histories to evaluate player performance
    best_score = env.reward_range[0]
    score_history = []
    avg_score_history = []

    # if using the saved weights and biases
    load_checkpoint = True

    # if we want to render the environment
    to_render = True

    # load weights and biases
    if load_checkpoint:
        agent.load_models()

    # run for some number of games
    for i in range(n_games):

        # reset current epoch
        observation = env.reset()
        done = False
        score = 0

        # while the agent is still playing the game
        while not done:

            # render the environment
            if to_render and (i % 1 == 0):
                env.render()
                time.sleep(0.05)

            # use the policy to choose an action
            action = agent.choose_action(observation)

            # get information from the environment
            observation_new, reward, done, info = env.step(action)

            # update the score with the reward
            score += reward

            # if we are not loading weights then learn the weights
            if not load_checkpoint:
                agent.learn(observation, reward, observation_new, done)

            # prepare for next timestep in the game
            observation = observation_new

        # build score history to show the learning curves
        score_history.append(score)
        avg_score = np.mean(score_history[-100:])
        avg_score_history.append(avg_score)

        # if the model is really good then save the weights
        if avg_score > best_score:
            best_score = avg_score
            if not load_checkpoint:
                agent.save_models()

        # print to see agent performance
        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score)


    # end the render
    if to_render:
        env.close()




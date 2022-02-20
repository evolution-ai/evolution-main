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

# from actor_critic_basic.utils import plot_learning_curve

from ac1_actors import Agent


def plot_learning_curve(x, scores, figure_file):
    running_avg = np.zeros(len(scores))
    for i in range(len(running_avg)):
        running_avg[i] = np.mean(scores[max(0, i-100):(i+1)])
    plt.plot(x, running_avg)
    plt.title('Running average of previous 100 scores')
    plt.savefig(figure_file)


if __name__ == '__main__':

    env = gym.make('CartPole-v1')

    agent = Agent(alpha = 1e-5, n_actions=env.action_space.n)
    n_games = 5

    filename = 'cartpole.png'
    figure_file = 'plots/' + filename

    best_score = env.reward_range[0]
    score_history = []
    avg_score_history = []
    load_checkpoint = True
    to_render = True

    if load_checkpoint:
        agent.load_models()

    for i in range(n_games):

        observation = env.reset()
        done = False
        score = 0

        while not done:

            if to_render and (i % 1 == 0):
                env.render()
                time.sleep(0.05)

            action = agent.choose_action(observation)
            observation_n, reward, done, info = env.step(action)

            score += reward

            if not load_checkpoint:
                agent.learn(observation, reward, observation_n, done)

            observation = observation_n

        score_history.append(score)
        avg_score = np.mean(score_history[-100:])
        avg_score_history.append(avg_score)

        if avg_score > best_score:

            best_score = avg_score

            if not load_checkpoint:
                agent.save_models()

        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score)


    if to_render:
        env.close()

    # x = [i+1 for i in range(n_games)]
    # plot_learning_curve(x, score_history, figure_file)
    # print(score_history)



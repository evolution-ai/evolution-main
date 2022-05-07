import os
from pickletools import optimize
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import tensorflow as tf
import gym
import tensorflow_probability as tfp
import time
from actors import Agent


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

    ## HYPER PARAMETERS
    alpha = 0.0001
    n_episodes = 500

    # if using the saved weights and biases
    load_checkpoint = False

    # if we want to render the environment
    to_render = False


    # call the open AI gym environment
    env = gym.make('CartPole-v1')

    # create an actor
    agent = Agent(alpha = alpha, n_actions=env.action_space.n, name="ac-cartpole-")
    

    # for file saves only
    filename = 'cartpole.png'
    figure_file = 'plots/' + filename

    # create score histories to evaluate player performance
    best_score = env.reward_range[0]
    score_history = []
    entropy_history = []
    avg_score_history = []
    avg_entropy_history = []

    # load weights and biases
    if load_checkpoint:
        agent.load_models()

    # run for some number of games
    for i in range(n_episodes):

        # reset current episode
        observation = env.reset()
        done = False
        score = 0
        episode_length = 0
        total_entropy = 0

        # while the agent is still playing the game
        while not done:

            # render the environment
            if to_render and (i % 1 == 0):
                env.render()
                time.sleep(0.05)

            # use the policy to choose an action
            action, entropy = agent.choose_action(observation)

            # get information from the environment
            observation_new, reward, done, info = env.step(action)

            # update the score with the reward
            score += reward

            # update episode length
            episode_length += 1

            # update the total entropy
            total_entropy += entropy

            # if we are not loading weights then learn the weights
            if not load_checkpoint:
                agent.learn(observation, reward, observation_new, done)

            # prepare for next timestep in the game
            observation = observation_new

        # build score history to show the learning curves
        score_history.append(score)
        episodic_entropy = total_entropy/episode_length
        entropy_history.append(episodic_entropy)

        avg_score = np.mean(score_history[-10:])
        avg_score_history.append(avg_score)

        avg_entropy = np.mean(entropy_history[-10:])
        avg_entropy_history.append(avg_entropy)

        # if the model is really good then save the weights
        if avg_score > best_score:
            best_score = avg_score
            if not load_checkpoint:
                agent.save_models()

        # print to see agent performance
        print('episode ', i, 'score %.1f' % score, 'avg_score %.1f' % avg_score, 
            'avg_entropy %.2f' % avg_entropy)


    # end the render
    if to_render:
        env.close()


    np.savetxt("a0001_e500_1.csv", [avg_score_history, avg_entropy_history], delimiter =" ",  fmt ='% s')

    plt.plot(avg_score_history)
    plt.plot(avg_entropy_history)
    plt.show()
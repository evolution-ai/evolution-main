import gym
import time


env = gym.make('CartPole-v0')

for i_episode in range(1):

    observation = env.reset()

    for t in range(1000):
        env.render()
        action = env.action_space.sample()

        observation, reward, done, info = env.step(action)

        time.sleep(0.002)

        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break

env.close()
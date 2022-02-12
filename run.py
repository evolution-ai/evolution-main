import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame
from basic_room import Room
from basic_agent import *
import os
import time

## Class definition:
# This class describes the game which contains both the game and the list of 
# agents 
## Fields:
# - room: stores a representation of a room
# - agents: a list of agents in the room 
# Methods:
# - play:

class Game:

    def __init__(self) -> None:

        self.x_length = 500
        self.y_length = 500
        self.goal_radius = 2

        # room size is same as pygame display
        # predators is a list of predator agents 
        # prey is a list of prey agents 

        self.preys = [Basic_Prey_Agent(250, 250, self.goal_radius)]
        self.predators = [Basic_Predator_Agent(30, 30, self.preys)]

        self.room = Room(self.x_length, self.y_length, self.goal_radius, self.preys)
        ##self.agents = [Basic_Agent(30, 30)]

        

    def play(self):
        for agent in self.predators:
            agent.naive_move()

    # TODO: read up on pygame
    def run(self):

        pygame.init()

        # make room size global variables?
        screen = pygame.display.set_mode([self.x_length, self.y_length])
        running = True
        
        while running:

            self.play()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            screen.fill((255, 255, 255))

            # Draw a solid blue circle for the goal
            
            for prey_agent in self.preys:
                prey_agent.random_move()
                pygame.draw.circle(screen, (0, 0, 255), (prey_agent.current_x, prey_agent.current_y), self.goal_radius)

            # TODO: clean this up
            agent = self.predators[0]

            current_x = agent.current_x
            current_y = agent.current_y

            os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (current_x,current_y)
            os.environ['SDL_VIDEO_CENTERED'] = '0'

            # 0 0 should be bottom left corner
            pygame.draw.circle(screen, (255, 0, 0), 
                (current_x, self.y_length - current_y), 10)
            
            # Flip the display
            pygame.display.flip()

            if self.room.is_goal(current_x, current_y):
                time.sleep(5)
                pygame.quit()
        
        pygame.quit()
            
        
if __name__ == "__main__":
    game = Game()
    game.run()
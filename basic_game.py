import math
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygame
from basic_room import Room
from basic_agent import Basic_Agent
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
        self.goal_radius = 10

        # room size is same as pygame display
        self.room = Room(self.x_length, self.y_length, self.goal_radius)
        self.agents = [Basic_Agent(30, 30)]

    def play(self):
        for agent in self.agents:
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

            # Draw a solid blue circle in the center - goal 
            pygame.draw.circle(screen, (0, 0, 255), (self.room.x_goal, self.room.y_goal), self.goal_radius)

            # TODO: clean this up
            agent = self.agents[0]

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
            
        
if __name__ == "__main__":
    game = Game()
    game.run()
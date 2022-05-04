import pygame, numpy
from painter import PyGamePainter

# Dimension Definitions
SCREEN_WIDTH, SCREEN_HEIGHT = (800,800)
# PLATFORM_WIDTH, PLATFORM_HEIGHT = (2000,2000)

# Other Definitions
NAME = "Evolution AI"
VERSION = "0.01"

AGENT = 1
FOOD = 2

class Visualizer:
    def __init__(self):
        self.painter = PyGamePainter()
        
    def display(self, agents_lst, food_dict):
        self.painter.clear_display()

        for agent in agents_lst:
            norm_x = (agent.pos[0]*4)+400
            norm_y = (agent.pos[1]*4)+400
            self.painter.draw((AGENT, (norm_x, norm_y), {"energy" : agent.energy, "max_energy" : agent.max_energy}))

        for food_pos in food_dict.keys():
            norm_x = (food_pos[0]*4)+400
            norm_y = (food_pos[1]*4)+400
            self.painter.draw((FOOD, (norm_x, norm_y), {}))

        self.painter.paint()

        return 
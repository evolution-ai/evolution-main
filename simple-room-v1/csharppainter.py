import clr
clr.AddReference(r'Library.dll')
from Library import Wrapper
wrapper = Wrapper()
import pygame, numpy

# Dimension Definitions
SCREEN_WIDTH, SCREEN_HEIGHT = (800,800)

# Other Definitions
NAME = "Evolution AI"
VERSION = "0.01"

AGENT = 1
FOOD = 2

class CSharpPainter:
    """Used to organize the drawing/ updating procedure.
    Implemantation based on Strategy Pattern.
    Note that Painter draws objects in a FIFO order.
    Objects added first, are always going to be drawn first.
    """

    def __init__(self):
        self.paintings = []

    def clear_display(self):
        self.surface.fill((255,255,255))

    def paint(self):
        pygame.display.flip()
    
    def draw(self, drawing):
        if drawing[0] == AGENT:
                self.draw_agent(drawing[1], drawing[2])
        elif drawing[0] == FOOD:
                self.draw_food(drawing[1])

    def draw_food(self, pos):
        pygame.draw.circle(self.surface, (255,0,0), pos, 1)

    def draw_agent(self, pos, args):
        pygame.draw.circle(self.surface, (0,0,255), pos, 3)
        self.draw_health_bar(pos, args["energy"], args["max_energy"])

    def draw_health_bar(self, pos, energy, max_energy): 
        pygame.draw.rect(self.surface, (255,0,0), pygame.Rect((pos[0], pos[1]), (1*int(max_energy), 6)))
        pygame.draw.rect(self.surface, (0,255,0), pygame.Rect((pos[0], pos[1]), (1*int(energy), 6)))
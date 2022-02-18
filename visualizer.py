import pygame, numpy

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
        self.painter = Painter()
        
    def display(self, agents_pos, food_dict):
        self.painter.clear_display()

        for i in range(agents_pos.shape[0]):
            norm_x = (agents_pos[i][0]*4)+400
            norm_y = (agents_pos[i][1]*4)+400
            self.painter.draw((AGENT, (norm_x, norm_y)))

        for food_pos in food_dict.keys():
            norm_x = (food_pos[0]*4)+400
            norm_y = (food_pos[1]*4)+400
            self.painter.draw((FOOD, (norm_x, norm_y)))

        self.painter.paint()

        return 

class Painter:
    """Used to organize the drawing/ updating procedure.
    Implemantation based on Strategy Pattern.
    Note that Painter draws objects in a FIFO order.
    Objects added first, are always going to be drawn first.
    """

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("{} - v{}".format(NAME, VERSION))
        clock = pygame.time.Clock()
        try:
            font = pygame.font.Font("Ubuntu-B.ttf",20)
            big_font = pygame.font.Font("Ubuntu-B.ttf",24)
        except:
            print("Font file not found: Ubuntu-B.ttf")
            font = pygame.font.SysFont('Ubuntu',20,True)
            big_font = pygame.font.SysFont('Ubuntu',24,True)
        self.surface = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.paintings = []

    def clear_display(self):
        self.surface.fill((255,255,255))

    def paint(self):
        pygame.display.flip()
    
    def draw(self, drawing):
        if drawing[0] == AGENT:
                self.draw_agent(drawing[1])
        elif drawing[0] == FOOD:
                self.draw_food(drawing[1])

    def draw_food(self, pos):
        pygame.draw.circle(self.surface, (255,0,0), pos, 1)

    def draw_agent(self, pos):
        pygame.draw.circle(self.surface, (0,0,255), pos, 1)
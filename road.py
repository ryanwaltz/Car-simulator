import math
import pygame
import config


class Road:
    def __init__(self, lanes, color, start_pos, vertical):
        self.lanes = lanes
        self.color = color
        self.start_pos = start_pos
        self.vertical = vertical
        self.lane_size = 30

    def blit(self, screen):
        if self.vertical:
            x = self.start_pos - self.lane_size * 1.5
            pygame.draw.rect(screen, self.color, (x, 0, self.lane_size * 3, config.window[1]))
        else:
            y = self.start_pos - self.lane_size * 1.5
            pygame.draw.rect(screen, self.color, (0, y, config.window[0], self.lane_size * 3))

    def blit_lines(self, screen):
        if self.vertical:
            pygame.draw.line(screen, (255, 98, 56), (self.start_pos - self.lane_size / 2, 0),
                             (self.start_pos - self.lane_size / 2, config.window[1]))
            pygame.draw.line(screen, (255, 98, 56), (self.start_pos + self.lane_size / 2, 0),
                             (self.start_pos + self.lane_size / 2, config.window[1]))
        else:
            pygame.draw.line(screen, (255, 98, 56), (0, self.start_pos - self.lane_size / 2),
                             (config.window[0], self.start_pos - self.lane_size / 2))
            pygame.draw.line(screen, (255, 98, 56), (0, self.start_pos + self.lane_size / 2),
                             (config.window[0], self.start_pos + self.lane_size / 2))

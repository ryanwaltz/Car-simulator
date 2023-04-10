import math
import pygame
import config


class Intersection:
    def __init__(self, road1, road2, color, stoplight_operation=False):
        self.road1 = road1
        self.road2 = road2
        if road1.vertical ^ road2.vertical:
            pass
        else:
            raise KeyboardInterrupt
        if road1.vertical:
            self.pos = [road1.start_pos, road2.start_pos]
        else:
            self.pos = [road2.start_pos, road1.start_pos]
        self.color = color
        self.priority = None
        self.white_listed = []
        self.second_priority = []
        self.priority_angle = 0
        self.matrix = [[0, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]]
        self.green_lighted = []
        self.stoplight_operation = stoplight_operation
        self.stoplight_right_of_way = []

        if self.stoplight_operation:
            self.stoplight_right_of_way = [False, 0]

    def blit(self, screen):
        if self.road1.lanes == 3 and self.road2.lanes == 3:
            pygame.draw.rect(screen, self.color, (self.pos[0] - 45, self.pos[1] - 45, 90, 90))

            pygame.draw.polygon(screen, (255, 255, 255), points=((self.pos[0] + 45, self.pos[1] + 45),
                                                                 (self.pos[0] + 75, self.pos[1] + 45),
                                                                 (self.pos[0] + 45, self.pos[1] + 75)))

            pygame.draw.polygon(screen, (255, 255, 255), points=((self.pos[0] - 45, self.pos[1] + 45),
                                                                 (self.pos[0] - 75, self.pos[1] + 45),
                                                                 (self.pos[0] - 45, self.pos[1] + 75)))

            pygame.draw.polygon(screen, (255, 255, 255), points=((self.pos[0] + 45, self.pos[1] - 45),
                                                                 (self.pos[0] + 75, self.pos[1] - 45),
                                                                 (self.pos[0] + 45, self.pos[1] - 75)))

            pygame.draw.polygon(screen, (255, 255, 255), points=((self.pos[0] - 45, self.pos[1] - 45),
                                                                 (self.pos[0] - 75, self.pos[1] - 45),
                                                                 (self.pos[0] - 45, self.pos[1] - 75)))

    def regulate_stoplight(self):
        for car in config.cars:
            if car.road.vertical == self.stoplight_right_of_way[0]:
                if len(car.intent) != 0:
                    if car.intent[1] != -1:
                        car.stop_on_intersection = False
                        print("car can go now")
                    else:
                        car.stop_on_intersection = self
                else:
                    car.stop_on_intersection = self
            else:
                car.stop_on_intersection = self

    def switch_stoplight(self):
        if self.stoplight_operation:
            for car in config.cars:
                car.stop_on_intersection = False
            self.stoplight_right_of_way[0] = not self.stoplight_right_of_way[0]

    def regulate(self):
        if self.stoplight_operation:
            self.regulate_stoplight()
            return
        lowest = 1000000
        if self.priority is None:
            self.matrix = [[0, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]]
            for car in config.cars:
                car.velocity = 1
                if car not in self.white_listed:
                    if math.sqrt((car.pos[0] - self.pos[0]) ** 2 + (car.pos[1] - self.pos[1]) ** 2) < lowest:
                        lowest = math.sqrt((car.pos[0] - self.pos[0]) ** 2 + (car.pos[1] - self.pos[1]) ** 2)
                        self.priority = car
            if self.priority is not None:
                self.priority.color = (0, 255, 0)
                self.priority.velocity = 1
                self.priority.stop_on_intersection = False
                if len(self.priority.intent) != 0:
                    self.matrix = self.priority.path
                    self.second_priority = []
                    self.green_lighted = [[self.priority.intent[0], self.priority.intent[1], self.priority.initial_angle]]
                    if self.priority.intent[1] == 0:
                        self.green_lighted.append([self.priority.intent[0], 1, self.priority.initial_angle])  # adjustment of self.greenlighted is necessary because intent can be interpreted different ways with an angle attached.
                        #                                                                                       this doesn't make a problem within Car functions, but it does here.

                    for car in self.get_lowest_from_distance():
                        if car == self.priority or car in self.white_listed or car in self.second_priority:
                            pass
                        else:
                            if len(car.intent) != 0:
                                if self.combine(car):
                                    self.matrix = self.combine(car)
                                    self.second_priority.append(car)
                                    self.green_lighted.append([car.intent[0], car.intent[1], car.initial_angle])
                                    if car.intent[1] == 0:
                                        self.green_lighted.append([car.intent[0], 1, car.initial_angle])
                                    car.stop_on_intersection = False
                                elif [car.intent[0], car.intent[1], car.initial_angle] in self.green_lighted:
                                    self.second_priority.append(car)
                                    car.stop_on_intersection = False
            else:
                return
        else:
            for car in config.cars:
                if car == self.priority or car in self.white_listed or car in self.second_priority:
                    pass
                else:
                    car.stop_on_intersection = self
        try:
            if len(self.priority.intent) == 0:
                self.white_listed.append(self.priority)
                self.priority.color = (0, 0, 255)

                self.priority = None

                self.second_priority = []
        except AttributeError:
            self.white_listed.append(self.priority)
            self.priority.color = (0, 0, 255)
            self.priority = None

    @staticmethod
    def calculate_efficiency(list_of_cars):
        largest_time = 0
        for car in list_of_cars:
            pass

    def combine(self, second_priority_temp):
        return_matrix = [[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]]
        for valuey, ii in enumerate(second_priority_temp.path):
            for valuex, iii in enumerate(ii):
                if valuex == 1 and valuey == 1:
                    if type(self.matrix[1][1]) is int:
                        return_matrix[1][1] = iii
                    elif type(iii) is int:  # fixing bugs
                        return_matrix[1][1] = self.matrix[1][1]
                    elif self.matrix[1][1] == iii and type(self.matrix[1][1]) == type(iii):
                        return_matrix[1][1] = iii
                    else:
                        return False
                elif self.matrix[valuey][valuex] == 1 and iii == 1:
                    return False
                else:
                    return_matrix[valuey][valuex] = self.matrix[valuey][valuex] + iii
        return return_matrix

    def get_lowest_from_distance(self):  # returns a list sorted by the lowest distance to the intersection
        lowest = 10000
        priority = None
        checked = []
        last_car = None
        _return = True
        while True:
            for car in config.cars:
                if car not in self.white_listed and car not in self.second_priority and car is not self.priority and car not in checked:
                    if self.get_distance_horizontal_vertical(car) < lowest:
                        lowest = self.get_distance_horizontal_vertical(car)
                        last_car = priority
                        priority = car
                    _return = False
            if _return:
                return checked
            _return = True
            lowest = 10000
            if last_car == priority:
                return checked
            checked.append(priority)

    def distance(self, car):
        return math.sqrt((car.pos[0] - self.pos[0]) ** 2 + (car.pos[1] - self.pos[1]) ** 2)

    def get_distance_horizontal_vertical(self, car):
        if car.road.vertical:
            return abs(car.pos[1]-self.pos[1])
        else:
            return abs(car.pos[0] - self.pos[0])

import math
import pygame
import config
import time


def normalize_angle(angle):
    if angle >= 2*math.pi:
        return angle - 2*math.pi
    if angle < -math.pi/2:
        return angle + 2*math.pi
    return angle


class Intersection:
    def __init__(self, road1, road2, color):
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

    def regulate(self):
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


class Car:
    def __init__(self, color, position, angle, length, width, velocity, road=None, lane=None, intent=None, iterator=0):
        self.color = color
        self.pos = position
        self.angle = angle
        self.length = length
        self.width = width
        self.velocity = velocity
        self.road = road
        self.lane = lane
        self.target_lane = None
        self.previous_angle = angle
        self.has_turned = False
        if self.road.vertical:
            self.pos = [self.road.start_pos + (self.lane - self.road.lanes + 1) * self.road.lane_size, position[1]]
        else:
            self.pos = [position[0], self.road.start_pos + (self.lane - self.road.lanes + 1) * self.road.lane_size]
        self.turning = False
        self.desired_position = [0, 0]
        self.circle_radius = 0
        self.circle_center = [0, 0]
        self.new_angle = 0
        self.adjustment = 1
        self.adjustment_case = 0
        self.initial_angle = angle
        if intent is None:
            self.intent = []
        else:
            self.intent = intent  # should be a list with the intersection and which way you want to turn (-1 for left, 0 for straight, 1 for right)
        self.stop_on_intersection = False
        self.start_time = iterator
        self.path = self.createpath()
        self.corners = []

    def createpath(self):
        if self.angle == 0:
            if self.intent[1] == 0:
                return [[0, 0, 0],
                       [0, 0, 0],
                       [1, 1, 1]]
            elif self.intent[1] == 1:
                return [[0, 0, 0],
                       [0, 0, 0],
                       [1, 0, 0]]
            else:
                return [[0, 0, 1],
                       [1, True, 0],
                       [0, 0, 0]]
        elif self.angle == -math.pi/2:
            if self.intent[1] == 0:
                return [[1, 0, 0],
                        [1, 0, 0],
                        [1, 0, 0]]
            elif self.intent[1] == 1:
                return [[1, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0]]
            else:
                return [[0, 1, 0],
                        [0, False, 0],
                        [0, 0, 1]]
        elif self.angle == math.pi:
            if self.intent[1] == 0:
                return [[1, 1, 1],
                        [0, 0, 0],
                        [0, 0, 0]]
            elif self.intent[1] == 1:
                return [[0, 0, 1],
                        [0, 0, 0],
                        [0, 0, 0]]
            else:
                return [[0, 0, 0],
                        [0, True, 1],
                        [1, 0, 0]]
        elif self.angle == math.pi/2:
            if self.intent[1] == 0:
                return [[0, 0, 1],
                        [0, 0, 1],
                        [0, 0, 1]]
            elif self.intent[1] == 1:
                return [[0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 1]]
            else:
                return [[1, 0, 0],
                        [0, False, 0],
                        [0, 1, 0]]

    def blit(self, screen):
        self.angle = -self.angle
        angle_to_top_right = math.tan(self.width / self.length) + self.angle

        angle_to_bottom_right = math.tan(-self.width / self.length) + self.angle

        angle_to_top_left = math.pi + angle_to_bottom_right

        angle_to_bottom_left = math.pi + angle_to_top_right

        distance = math.sqrt((self.length / 2) ** 2 + (self.width / 2) ** 2)

        top_right_x = math.cos(angle_to_top_right) * distance
        top_right_y = math.sin(angle_to_top_right) * distance

        top_left_x = math.cos(angle_to_top_left) * distance
        top_left_y = math.sin(angle_to_top_left) * distance

        bottom_right_x = math.cos(angle_to_bottom_right) * distance
        bottom_right_y = math.sin(angle_to_bottom_right) * distance

        bottom_left_x = math.cos(angle_to_bottom_left) * distance
        bottom_left_y = math.sin(angle_to_bottom_left) * distance

        self.corners = [
            [bottom_right_x + self.pos[0], bottom_right_y + self.pos[1]],
            [top_right_x + self.pos[0], top_right_y + self.pos[1]],
            [top_left_x + self.pos[0], top_left_y + self.pos[1]],
            [bottom_left_x + self.pos[0], bottom_left_y + self.pos[1]],
        ]
        self.angle = -self.angle

        pygame.draw.polygon(screen, self.color, self.corners)
        pygame.draw.line(screen, (0, 255, 0), start_pos=self.corners[0], end_pos=self.corners[1])

    def turn(self, angle):
        self.angle += angle

    def move(self, time):
        if self.velocity == 0:
            return
        if self.turning:
            self.turning_func(time)
            return
        if self.target_lane is not None:
            self.angle = -self.angle
            distance_x = self.velocity / time * math.cos(self.angle)
            distance_y = self.velocity / time * math.sin(self.angle)
            if self.road.vertical:
                if (self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos > self.pos[0]:
                    if self.pos[0] + distance_x >= (
                            self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos:
                        distance_x_new = (self.pos[0] + distance_x) - ((
                                                                               self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos)
                    else:
                        self.pos[0] += distance_x
                        self.pos[1] += distance_y

                        self.angle = -self.angle
                        return
                elif (self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos < self.pos[0]:
                    if self.pos[0] + distance_x <= (
                            self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos:
                        distance_x_new = ((
                                                      self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos) - (
                                                     self.pos[0] + distance_x)
                    else:
                        self.pos[0] += distance_x
                        self.pos[1] += distance_y

                        self.angle = -self.angle
                        return
                else:
                    self.pos[0] += distance_x
                    self.pos[1] += distance_y

                    self.angle = -self.angle
                    return

                distance_total_new = distance_x_new / math.cos(self.angle)
                distance_y_new = distance_total_new * math.cos(self.angle)

                self.pos[0] += distance_x_new
                self.pos[1] += distance_y_new
                self.lane = self.target_lane
                self.target_lane = None

                self.angle = self.previous_angle

            else:
                if (self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos > self.pos[1]:
                    if self.pos[1] + distance_y >= (
                            self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos:
                        distance_y_new = (self.pos[1] + distance_y) - ((
                                                                                   self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos)
                    else:
                        self.pos[0] += distance_x
                        self.pos[1] += distance_y

                        self.angle = -self.angle
                        return

                elif (self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos < self.pos[1]:
                    if self.pos[1] + distance_y <= (
                            self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos:
                        distance_y_new = ((
                                                      self.target_lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos) - (
                                                     self.pos[1] + distance_y)
                    else:
                        self.pos[0] += distance_x
                        self.pos[1] += distance_y

                        self.angle = -self.angle
                        return
                else:
                    self.pos[0] += distance_x
                    self.pos[1] += distance_y

                    self.angle = -self.angle
                    return
                # this warning shouldn't be triggered
                distance_total_new = distance_y_new / math.sin(self.angle)

                distance_x_new = distance_total_new * math.cos(self.angle)

                self.pos[0] += distance_x_new
                self.pos[1] += distance_y_new
                self.lane = self.target_lane
                self.target_lane = None

                self.angle = self.previous_angle

            self.pos[0] += distance_x
            self.pos[1] += distance_y

            self.angle = -self.angle
        else:
            self.check_movement()
            self.angle = -self.angle
            distance_x = self.velocity / time * math.cos(self.angle)
            distance_y = self.velocity / time * math.sin(self.angle)
            if self.stop_on_intersection:  # this block stops in front of the intersection - not in front of the other cars
                try:
                    if self.intent[0].vertical:
                        distance = abs(self.pos[0] - self.stop_on_intersection.pos[0]) - (45 if self.lane != 2 else 50) - self.length / 2
                        if distance < abs(distance_x):
                            distance_x = distance * (distance_x / abs(distance_x))
                            self.velocity = 0
                    else:
                        distance = abs(self.pos[1] - self.stop_on_intersection.pos[1]) - (45 if self.lane != 2 else 50) - self.length / 2
                        if distance < abs(distance_y):
                            distance_y = distance * (distance_y / abs(distance_y))
                            self.velocity = 0
                except IndexError:
                    pass

            self.pos[0] += distance_x
            self.pos[1] += distance_y

            self.angle = -self.angle

    def check_movement(self):
        if len(self.intent) == 0:
            return
        else:
            adjusted = False
            for car in config.cars:
                if car.lane == self.lane and car.angle == self.angle:
                    if car.velocity == 0:
                        if config.intersections[0].distance(self) > config.intersections[0].distance(car):
                            if self.intent[0].vertical:
                                if abs(self.pos[0] - car.pos[0]) < self.length + 10:
                                    self.velocity = 0
                                    adjusted = True
                                    break
                                else:
                                    self.velocity = 1
                            else:
                                if abs(self.pos[1] - car.pos[1]) < self.length + 10:
                                    self.velocity = 0
                                    adjusted = True
                                    break
                                else:
                                    self.velocity = 1
            if adjusted is False:
                self.velocity = 1
            try:
                if self.intent[1] == -1 and self.lane != 2:
                    self.lane_change_start(2, 500)
                if self.intent[1] == -1 and self.lane == 2:
                    if self.road.vertical:
                        if self.angle == math.pi / 2:
                            lane = 1
                        else:
                            lane = 3
                    else:
                        if self.angle == 0:
                            lane = 3
                        else:
                            lane = 1
                    if self.intent[0].vertical:
                        iterator = 0
                        adjustment = 1
                    else:
                        iterator = 1
                        adjustment = -1
                    if abs(self.pos[iterator] - self.intent[0].start_pos) < 47.5:
                        self.turn_start(lane, self.intent[0], new_angle=self.angle - adjustment * (math.pi / 2))
                if self.intent[1] == 1:
                    if self.road.vertical:
                        if self.angle == math.pi / 2:
                            lane = 3
                        else:
                            lane = 1
                    else:
                        if self.angle == 0:
                            lane = 1
                        else:
                            lane = 3
                    if self.angle == 0 or self.angle == math.pi:
                        adjustment = -1
                    else:
                        adjustment = 1
                    if self.intent[0].vertical:
                        iterator = 0
                    else:
                        iterator = 1
                    if abs(self.pos[iterator] - self.intent[0].start_pos) < 50:
                        self.turn_start(lane, self.intent[0],
                                        new_angle=self.angle - adjustment * (math.pi / 2))  # dirty hacks
                if self.intent[1] == 0:
                    if self.angle == 0:
                        if self.pos[0] - self.intent[0].start_pos > 45:
                            self.intent = []
                    elif self.angle == math.pi:
                        if self.pos[0] - self.intent[0].start_pos < -45:
                            self.intent = []
                    elif self.angle == -math.pi / 2 or self.angle == 3 * math.pi / 2:
                        if self.pos[1] - self.intent[0].start_pos > 45:
                            self.intent = []
                    else:  # math.pi/2
                        if self.pos[1] - self.intent[0].start_pos < -45:
                            self.intent = []

            except IndexError:
                self.intent = []

    def check_collision(self, car):
        distance_to_get_ordinary_angle = -self.angle
        car_angle = distance_to_get_ordinary_angle + car.angle
        self_angle = distance_to_get_ordinary_angle + self.angle

        angle_from_self_to_car = math.atan2(self.pos[1]-car.pos[1], self.pos[0] - car.pos[0])

        distance = math.sqrt((self.pos[1]-car.pos[1])**2 + (self.pos[0]-car.pos[0]**2))

        adjusted_angle_from_self_to_car = angle_from_self_to_car + distance_to_get_ordinary_angle

        car_pos = [self.pos[0] + distance * math.cos(adjusted_angle_from_self_to_car), self.pos[1] + distance * math.sin(adjusted_angle_from_self_to_car)]

        angle_to_top_right_self = math.tan(self.width / self.length) + self_angle

        angle_to_bottom_right_self = math.tan(-self.width / self.length) + self_angle

        angle_to_top_left_self = math.pi + angle_to_bottom_right_self

        angle_to_bottom_left_self = math.pi + angle_to_top_right_self

        distance = math.sqrt((self.length / 2) ** 2 + (self.width / 2) ** 2)

        top_right_x_self = math.cos(angle_to_top_right_self) * distance
        top_right_y_self = math.sin(angle_to_top_right_self) * distance

        top_left_x_self = math.cos(angle_to_top_left_self) * distance
        top_left_y_self = math.sin(angle_to_top_left_self) * distance

        bottom_right_x_self = math.cos(angle_to_bottom_right_self) * distance
        bottom_right_y_self = math.sin(angle_to_bottom_right_self) * distance

        bottom_left_x_self = math.cos(angle_to_bottom_left_self) * distance
        bottom_left_y_self = math.sin(angle_to_bottom_left_self) * distance

        self_corners = [
            [top_right_x_self+self.pos[0], top_right_y_self+self.pos[1]],
            [top_left_x_self+self.pos[0], top_left_y_self+self.pos[1]],
            [bottom_right_x_self+self.pos[0], bottom_right_y_self+self.pos[1]],
            [bottom_left_x_self+self.pos[0], bottom_left_y_self+self.pos[1]]
        ]

        angle_to_top_right_car = math.tan(self.width / self.length) + car_angle

        angle_to_bottom_right_car = math.tan(-self.width / self.length) + car_angle

        angle_to_top_left_car = math.pi + angle_to_bottom_right_car

        angle_to_bottom_left_car = math.pi + angle_to_top_right_car

        distance = math.sqrt((self.length / 2) ** 2 + (self.width / 2) ** 2)

        top_right_x_car = math.cos(angle_to_top_right_car) * distance
        top_right_y_car = math.sin(angle_to_top_right_car) * distance

        top_left_x_car = math.cos(angle_to_top_left_car) * distance
        top_left_y_car = math.sin(angle_to_top_left_car) * distance

        bottom_right_x_car = math.cos(angle_to_bottom_right_car) * distance
        bottom_right_y_car = math.sin(angle_to_bottom_right_car) * distance

        bottom_left_x_car = math.cos(angle_to_bottom_left_car) * distance
        bottom_left_y_car = math.sin(angle_to_bottom_left_car) * distance

        car_corners = [
            [top_right_x_car+car_pos[0], top_right_y_car+car_pos[1]],
            [top_left_x_car+car_pos[0], top_left_y_car+car_pos[1]],
            [bottom_right_x_car+car_pos[0], bottom_right_y_car+car_pos[1]],
            [bottom_left_x_car+car_pos[0], bottom_left_y_car+car_pos[1]]
        ]

        for i in car_corners:
            if self.corners[1][0] < i[0] < self.corners[0][0]:
                if self.corners[0][1] < i[1] < self.corners[2][1]:
                    print("collision detected")

    def align(self):
        if self.road.vertical:
            self.pos = [self.road.start_pos + (self.lane - self.road.lanes + 1) * self.road.lane_size, self.pos[1]]
        else:
            self.pos = [self.pos[0], self.road.start_pos + (self.lane - self.road.lanes + 1) * self.road.lane_size]

    def brake(self, power):
        if self.velocity < 5:
            self.velocity = 0
            return
        self.velocity *= 1 - power

    def accelerate(self, power):
        self.velocity *= 1 + power

    def lane_change_start(self, new_lane, distance):
        if self.lane is None:
            return
        if math.cos(self.angle) < 0:
            distance *= -1
        """elif math.sin(self.angle) < 0:
            distance *= -1"""
        if self.road.vertical:
            desired_position = [(new_lane - self.road.lanes + 1) * self.road.lane_size, self.pos[1] + distance]
        else:
            desired_position = [self.pos[0] + distance, (new_lane - self.road.lanes + 1) * self.road.lane_size]

        angle_to_shift_lanes = math.atan2(desired_position[1] - self.pos[1], desired_position[0] - self.pos[0])
        if not self.road.vertical and new_lane < self.lane:
            angle_to_shift_lanes *= -1
        elif self.road.vertical and new_lane > self.lane:
            angle_to_shift_lanes += math.pi
        self.target_lane = new_lane
        self.previous_angle = -self.angle
        self.angle = angle_to_shift_lanes
        self.lane = None

    def turn_start(self, lane, road, new_angle):  # road is desired road
        if road.vertical:
            pos_x = (lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos

            distance = abs(self.pos[0] - pos_x)

            distance_y = math.sin(new_angle) * distance

            if self.angle == math.pi and (self.new_angle == -math.pi / 2 or self.new_angle == 3 * math.pi / 2):
                distance_y *= -1
                self.adjustment = -1
                self.adjustment_case = 5

            if self.angle == 0 and (self.new_angle == -math.pi / 2 or self.new_angle == 3 * math.pi / 2):
                self.adjustment_case = 4
            if self.angle == 0 and self.new_angle == 0:
                self.adjustment_case = 5
            pos_y = self.pos[1] + distance_y

            circle_center = [self.pos[0], pos_y]
        else:
            pos_y = (lane - self.road.lanes + 1) * self.road.lane_size + self.road.start_pos

            distance = abs(self.pos[1] - pos_y)

            distance_x = math.cos(new_angle) * distance
            if (self.angle == -math.pi / 2 or self.angle == 3 * math.pi / 2) and (self.new_angle == 0):
                self.adjustment_case = 6

            pos_x = self.pos[0] + distance_x

            circle_center = [pos_x, self.pos[1]]

        desired_position = [pos_x, pos_y]

        circle_radius = abs(self.pos[0] - pos_x)

        self.turning = True

        self.desired_position = desired_position

        self.circle_radius = circle_radius

        self.circle_center = circle_center

        self.new_angle = new_angle

        if self.new_angle == -math.pi / 2 or self.new_angle == 3 * math.pi / 2:
            self.angle = -self.angle

        if self.new_angle == 0 and (self.angle == -math.pi / 2 or self.angle == 3 * math.pi / 2):
            self.adjustment_case = 3

        # equation of circle:  (x-desired_position[0])**2 + (y-desired_position[1])**2 = circle_radius**2

    def turning_func(self, time):
        self.angle = -self.angle
        distance_to_go = math.sqrt(
            (self.pos[0] - self.desired_position[0]) ** 2 + (self.pos[1] - self.desired_position[1]) ** 2)

        distance = self.velocity / time

        if distance_to_go < distance:
            self.pos = self.desired_position
            self.angle = -self.adjustment * self.new_angle
            self.turning = False
            self.adjustment_case = 0
            self.intent = []
            return

        angle_adjust = math.asin((distance / 2) / self.circle_radius)

        if self.new_angle * self.angle > 0:
            if self.new_angle > self.angle:
                new_angle = self.angle - math.pi / 2 + angle_adjust * 2
                self.turn(angle_adjust * 2)
                # angle adjust add to other angle
                pass
            else:
                new_angle = self.angle + math.pi / 2 - angle_adjust * 2
                self.turn(-angle_adjust * 2)
                # angle adjust subtract from other angle
                pass
        else:
            if self.new_angle == 0:
                if self.angle == math.pi / 2:
                    new_angle = self.angle + math.pi / 2 - angle_adjust * 2
                    self.turn(-angle_adjust * 2)
                    # subtract
                    pass
                else:
                    if self.adjustment_case == 3:
                        new_angle = self.angle + math.pi / 2 - angle_adjust * 2
                        self.turn(-angle_adjust * 2)
                    else:
                        new_angle = self.angle - math.pi / 2 + angle_adjust * 2
                        self.turn(angle_adjust * 2)
                    # add
                    pass
            else:
                if self.new_angle == math.pi / 2:
                    if self.adjustment_case == 5:
                        new_angle = self.angle - math.pi / 2 + angle_adjust * 2
                        self.turn(angle_adjust * 2)
                        # add
                        pass
                    else:
                        new_angle = self.angle + math.pi / 2 - angle_adjust * 2
                        self.turn(-angle_adjust * 2)
                        # subtract
                else:
                    if self.adjustment_case == 6:
                        new_angle = self.angle - math.pi / 2 + angle_adjust * 2
                        self.turn(angle_adjust * 2)
                    else:

                        new_angle = self.angle + math.pi / 2 - angle_adjust * 2
                        self.turn(-angle_adjust * 2)
                        # subtract
                        pass

        pos_x_diff = self.circle_radius * math.cos(new_angle)
        pos_y_diff = self.circle_radius * math.sin(new_angle)

        self.pos[0] = pos_x_diff + self.circle_center[0]
        self.pos[1] = pos_y_diff + self.circle_center[1]

        self.angle = -self.angle

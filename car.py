import math
import pygame
import config
import time


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
        self.turn_start_time = 0
        self.in_roundabout = False
        self.circle_pos = [0, 0]
        self.stop = False

    def in_intersection(self, intersection):
        if intersection.pos[0] - 47 < self.pos[0] < intersection.pos[0]+47:
            if intersection.pos[1] - 47 < self.pos[1] < intersection.pos[1] + 47:
                return True
        return False

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
        pygame.draw.circle(screen, (255, 0, 0), self.circle_pos, 4)
        """pygame.draw.line(screen, (255, 0, 0), self.circle_pos, self.pos)
        pygame.draw.line(screen, (255, 0, 0), self.pos, config.roundabouts[0].pos)
        pygame.draw.line(screen, (255, 0, 0), self.circle_pos, config.roundabouts[0].pos)"""

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
        elif len(config.intersections) != 0:
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
        else:
            if self.intent[0].vertical:
                iterator = 0
            else:
                iterator = 1
            if self.in_roundabout is False and not self.stop and math.sqrt((self.pos[0] - config.roundabouts[0].pos[0])**2 + (self.pos[1] - config.roundabouts[0].pos[1])**2) < 65:
                self.in_roundabout = True
                self.join_roundabout(config.roundabouts[0])
            if self.in_roundabout:
                self.join_roundabout(config.roundabouts[0])
                if self.check_exit():
                    self.in_roundabout = False
                    self.stop = True
                    print("i exited")
            elif self.exiting:
                self.check_lane_change()

    def check_lane_change(self):
        desired_angle = self.initial_angle - self.intent[1] * math.pi/2
        if desired_angle < 0:
            desired_angle += 2*math.pi
        road = self.intent[0]
        if road.vertical:
            if desired_angle == math.pi/2:
                pos = road.start_pos + 1.5*road.lane_size
            else:
                pos = road.start_pos - 1.5*road.lane_size
        else:
            if desired_angle == math.pi:
                pos = road.start_pos + 1.5*road.lane_size
            else:
                pos = road.start_pos - 1.5*road.lane_size


    def join_roundabout(self, roundabout):

        distance = math.sqrt((self.pos[0] - roundabout.pos[0])**2 + (self.pos[1] - roundabout.pos[1])**2)
        radius = roundabout.radius

        tangent_segment = math.sqrt(distance**2 - radius**2)

        angle_tangent_center = math.asin(radius/distance)
        angle_in_circle = math.asin(tangent_segment/distance)

        angle_in_tangent = math.pi - (angle_tangent_center + angle_in_circle)

        standard_angle_adjust = math.atan2(roundabout.pos[1]-self.pos[1], roundabout.pos[0]-self.pos[0])

        x_adjust = -math.cos(standard_angle_adjust-angle_in_circle)*radius
        y_adjust = -math.sin(standard_angle_adjust-angle_in_circle)*radius

        new_pos = [x_adjust+roundabout.pos[0], y_adjust+roundabout.pos[1]]

        get_angle = -(angle_tangent_center+standard_angle_adjust)

        """print(math.degrees(angle_in_tangent), "should be 90")
        print(math.degrees(angle_in_circle), "angle in circle")
        print(math.degrees(angle_tangent_center), "angle in point")
        print(math.degrees(standard_angle_adjust), "angle adjustment")
        print(math.degrees(get_angle), "new angle")
        print()"""
        self.angle = get_angle
        self.circle_pos = new_pos

    def check_exit(self):
        desired_angle = self.initial_angle - self.intent[1] * math.pi/2
        if self.angle < 0:
            angle = self.angle + 2*math.pi
        else:
            angle = self.angle
        if abs(angle+math.pi/4 - desired_angle) < math.pi/16:
            print("time to exit")
            print(desired_angle, angle)
            return True
        return False

    def exit_roundabout(self, lane, road):
        exit_pos = road.start_pos + (lane - road.lanes + 1) * road.lane_size

        desired_exit_position = []

        if road.vertical:
            distance_x = exit_pos - self.pos[0]
            normalized_angle = self.normalize_angle()

            distance_y = distance_x * math.tan(normalized_angle)

    def normalize_angle(self, angle):
        angle = self.angle
        if 0 < self.angle < math.pi/2:
            return self.angle
        elif math.pi/2 < self.angle <= math.pi:
            return math.pi - self.angle
        elif math.pi < self.angle <= 3*math.pi/2:
            return self.angle - math.pi
        else:
            return math.pi*2 - self.angle

    def check_collision(self, car):
        distance_to_get_ordinary_angle = -self.angle
        car_angle = distance_to_get_ordinary_angle + car.angle
        self_angle = distance_to_get_ordinary_angle + self.angle

        angle_from_self_to_car = math.atan2(self.pos[1]-car.pos[1], self.pos[0] - car.pos[0])

        distance = math.sqrt((self.pos[1]-car.pos[1])**2 + (self.pos[0]-car.pos[0])**2)

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
            if self_corners[1][0] < i[0] < self_corners[0][0]:
                if self_corners[0][1] < i[1] < self_corners[2][1]:
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

        self.turn_start_time += 1

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

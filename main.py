import pygame
import math
import random
import time
import config
from car import Car
from road import Road
from intersection import Intersection

pygame.init()

timekeeping = []
config.window = (800, 800)

screen = pygame.display.set_mode(config.window)
# testing to see if it will convert


def draw_screen():
    screen.fill((0, 0, 0))
    for i in config.roads:
        i.blit(screen)
    for i in config.roads:
        i.blit_lines(screen)
    for i in config.intersections:
        i.blit(screen)
        for valuey, ii in enumerate(i.matrix):
            for valuex, iii in enumerate(ii):
                if iii != 0:
                    pygame.draw.rect(screen, (0, 0, 255), (-45+30*valuex+i.pos[0], -45 + 30*valuey+i.pos[1], 30, 30))

    for i in config.cars:
        i.blit(screen)

    pygame.display.update()


def run():
    iterator = 0
    iterator_time = 0
    running = True
    now = time.time()
    while running:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_x]:
            config.cars.append(
                Car((255, 0, 0), [400, 400], angle=math.pi, length=50, width=20, velocity=1, road=config.roads[1],
                    lane=1, intent=[config.roads[0], 0]))
            time.sleep(0.1)
        for i in config.cars:
            """if i.angle < math.pi/2:
                i.turn(math.pi/64)"""
            i.move(1)
            if not(-20 < i.pos[0] < 820):
                config.cars.remove(i)
                calculate_time(i, iterator_time)
                iterator += 1
                if iterator > 100:
                    running = False
                    calculate_time_end()

            elif not(-20 < i.pos[1] < 820):
                config.cars.remove(i)
                calculate_time(i, iterator_time)
                iterator += 1
                if iterator > 100:
                    running = False
                    calculate_time_end()

            if not(355 < i.pos[0] < 445):
                if not(355 < i.pos[1] < 445):
                    print(i.lane, i.road.vertical, i.intent[0].vertical, i.intent[1], "this got screwed up", i.stop_on_intersection, i.velocity)
        """for i in config.cars:  # This serves no real purpose
            for ii in config.cars:
                if i != ii:
                    i.check_collision(ii)"""
        for i in config.intersections:
            i.regulate()
        if len(config.cars) == 0:
            try:
                spawn_new(iterator_time)
            except RecursionError:
                pass
        if random.randint(50, 100) == 69:
            try:
                spawn_new(iterator_time)
            except RecursionError:
                pass

        if time.time() > now + 15:
            config.intersections[0].switch_stoplight()
            print("switched stoplight")
            now = time.time()

        draw_screen()
        clock.tick(120)
        iterator_time += 1

    print(f"{iterator} cars have passed in {iterator_time/120} seconds")


def calculate_time(car, iterator_time):
    timekeeping.append(iterator_time - car.start_time)


def calculate_time_end():
    print(sum(timekeeping)/len(timekeeping)/120)


def spawn_new(iterator_time):
    random_number = random.randint(1, 4)
    if random_number == 1:
        position = [0, 430]
        road = 1
        intent_road = 0
        angle = 0
        lane = 3
    elif random_number == 2:
        position = [430, 800]
        angle = math.pi/2
        road = 0
        intent_road = 1
        lane = 3
    elif random_number == 3:
        position = [800, 370]
        road = 1
        angle = math.pi
        intent_road = 0
        lane = 1
    else:
        position = [370, 0]
        road = 0
        angle = -math.pi/2
        intent_road = 1
        lane = 1
    continue_create = True
    for car in config.cars:
        if math.sqrt((car.pos[0] - position[0])**2 + (car.pos[1] - position[1])**2) < 60:
            continue_create = False
            break
    if continue_create:
        config.cars.append(
            Car((255, 0, 0), position, angle, 50, 20, 1, road=config.roads[road], lane=lane, intent=[config.roads[intent_road], random.choice([1, 0, -1])], iterator=iterator_time)
        )
    else:
        spawn_new(iterator_time)


config.roads = [Road(lanes=3, color=(255, 255, 255), start_pos=400, vertical=True),
                Road(lanes=3, color=(255, 255, 255), start_pos=400, vertical=False)]


config.cars = [
    Car((255, 0, 0), [800, 800], angle=math.pi/2, length=50, width=20, velocity=1, road=config.roads[0], lane=3, intent=[config.roads[1], 1]),
    Car((255, 0, 0), [730, 730], angle=math.pi/2, length=50, width=20, velocity=1, road=config.roads[0], lane=3, intent=[config.roads[1], 0]),
        ]


config.intersections = [Intersection(config.roads[0], config.roads[1], (200, 200, 200), True)]

clock = pygame.time.Clock()
now = time.time()

run()

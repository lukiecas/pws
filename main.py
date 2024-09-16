import pygame
import random
import neat
import math
import numpy as np
from car import Car
from lidar_sensor import Lidar
pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True


NUM_RAYS = 20  # Number of LiDAR rays
FOV = 360  # Field of view in degrees (360 for full circle)
MAX_RANGE = 200  # Max range of LiDAR in pixels
LIDAR_ANGLE_STEP = FOV / NUM_RAYS  # Angular increment per ray

"""def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        # Here, you should simulate the car and use `net` to decide actions
        # for example: inputs = [lidar_data_1, lidar_data_2, lidar_data_3, lidar_data_4]
        inputs = distances  # Example data from LiDAR
        output = net.activate(inputs)
        # Calculate the fitness based on car behavior (e.g., lap time, distance covered)
        genome.fitness = compute_fitness(output)
def compute_fitness(output):
    # Implement your logic to compute fitness based on the control actions
    return fitness """
tracks = {"1" : ["track1.png", (420, 512)],}
track = pygame.image.load(tracks["1"][0]).convert()
car = Car(WIDTH, HEIGHT, tracks["1"][1])
lidar = Lidar(track, WIDTH, HEIGHT)
    
while running:
   
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    car.key_pressed(keys)
    car.handling()
    car.change_velocity()
    car.steering()
    x, y = car.report_position()
    distances, hit_points = lidar.simulate_lidar(x, y)
    
    for distance in distances:  
        if distance <= 0:
            car.has_died()
            print("car died")
    rotated_car, rotated_rect = car.moving_car()
    screen.blit(track, (0, 0))
    screen.blit(rotated_car, rotated_rect.topleft)
    if car.has_finished():
        print("track has been completed")
    # Update display
    pygame.display.flip()
    
    # Frame rate
    clock.tick(60)

pygame.quit()
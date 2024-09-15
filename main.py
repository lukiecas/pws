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
        
        # Initialize car and simulation here
        car = Car()  # Assume you have a Car class
        fitness = 0
        
        while not car.has_crashed():
            inputs = car.get_sensor_data()  # Get LiDAR, speed, etc.
            output = net.activate(inputs)
            
            car.steer(output[0])  # Steering
            car.throttle(output[1])  # Throttle
            
            car.update()
            fitness += car.get_distance_traveled()  # Add to fitness
            
        genome.fitness = fitness """
"""def run_neat():
    # Load configuration
    config_path = './config-feedforward'
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    # Create the population
    population = neat.Population(config)

    # Add a reporter for detailed stats
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run NEAT
    winner = population.run(eval_genomes, 50)  # Run for 50 generations
    print(f"Best genome: {winner}") """
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
    
    # Update display
    pygame.display.flip()
    
    # Frame rate
    clock.tick(60)

pygame.quit()
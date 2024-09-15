import pygame
import random
import neat
import math
import numpy as np
from car import Car
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
def cast_ray(x, y, angle):
    for i in range(MAX_RANGE):
        ray_x = int(x + i * math.cos(angle))
        ray_y = int(y + i * math.sin(angle))
        
        # Check if the ray is out of bounds
        if ray_x < 0 or ray_x >= WIDTH or ray_y < 0 or ray_y >= HEIGHT:
            return (ray_x, ray_y), i
        
        # Check if the ray hits a black pixel on the track
        if track.get_at((ray_x, ray_y)) == (255, 255, 255, 255):  # Black pixel (track)
            return (ray_x, ray_y), i
    
    # If no collision, return the maximum range
    return (int(x + MAX_RANGE * math.cos(angle)), int(y + MAX_RANGE * math.sin(angle))), MAX_RANGE
def simulate_lidar(x, y):
    distances = []
    rays = []
    
    for i in range(NUM_RAYS):
        angle = math.radians(i * LIDAR_ANGLE_STEP)  # Convert angle to radians
        hit_point, distance = cast_ray(x, y, angle)
        distances.append(distance)
        rays.append(hit_point)
    
    return distances, rays

            
    
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
    distances, hit_points = simulate_lidar(x, y)
    
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
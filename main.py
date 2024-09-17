import pygame
import random
import pickle
import neat
import math
import numpy as np
from car import Car
import pyautogui as pg
from lidar_sensor import Lidar

pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True


NUM_RAYS = 20  # Number of LiDAR rays
FOV = 360  # Field of view in degrees (360 for full circle)
MAX_RANGE = 200  # Max range of LiDAR in pixels
LIDAR_ANGLE_STEP = FOV / NUM_RAYS  # Angular increment per ray

tracks = {"1" : ["track1.png", (420, 512)],}
track = pygame.image.load(tracks["1"][0]).convert()
car_img = pygame.image.load("yellow-car-top-view-free-png.png").convert_alpha()  # Smaller car to represent RC car

def eval_genomes(genomes, config):
    num = 0
    for genome_id, genome in genomes:
        num+=1
        net = neat.nn.FeedForwardNetwork.create(genome, config) 
        car = Car(WIDTH, HEIGHT, tracks["1"][1], car_img)
        lidar = Lidar(track, WIDTH, HEIGHT)
        genome_fitness = 0
        running = True
        while running:
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            x, y, angle = car.report_position()
            distances, hit_points = lidar.simulate_lidar(x, y, -angle)
            normalized_distances = [d / MAX_RANGE for d in distances]
            output = net.activate(normalized_distances)
            steering = output[0]
            throttle = output[1]    
            
            keys = pygame.key.get_pressed()
            
            car.handling(throttle)
            car.change_velocity()
            car.steering(steering)
            
            
            for distance in distances:  
                if distance <= 0:
                    running = False
            genome.fitness = genome_fitness + car.get_distance_covered() / 1000.0
            rotated_car, rotated_rect = car.moving_car()
            screen.blit(track, (0, 0))
            screen.blit(rotated_car, rotated_rect.topleft)
            for hit_point in hit_points:
                if hit_points.index(hit_point) == 4 or hit_points.index(hit_point) == 12:
                
                    pygame.draw.line(screen, (0, 255, 0), (x, y), hit_point)
                else:
                    pygame.draw.line(screen, (255, 0, 0), (x, y), hit_point)

            if car.has_finished():
                print("track has been completed")
            # Update display
            text_surface = my_font.render(str(num), False, (0, 0, 0))
            screen.blit(text_surface, (0,0))
            fps_surface = my_font.render(str(round(clock.get_fps())), False, (0, 0, 0))
            screen.blit(fps_surface, (0,50))
            pygame.display.flip()
            # Frame rate
            clock.tick(5000)
            
def run_neat(config_file, checkpoint=None):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )

    # Create the population, which is the top-level object for a NEAT run
    
    
    if checkpoint:
        population = neat.Checkpointer.restore_checkpoint(checkpoint)
    else:
        population = neat.Population(config)

    # Add a reporter to show progress in the terminal
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(generation_interval=1, filename_prefix='neat-checkpoint-'))


    # Run for up to 50 generations
    winner = population.run(eval_genomes, 3)
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)
    # Display the winning genome
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    config_path = "config-feedforward.txt"  # Path to your NEAT config file
    checkpoint_file = 'neat-checkpoint-4'
    run_neat(config_path, checkpoint_file)
    pygame.quit()
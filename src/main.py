import pygame
import random
import pickle
import neat
import math
import time
import numpy as np
from car import Car
import pyautogui as pg
from lidar_sensor import Lidar
import matplotlib.pyplot as plt
import visualize
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
hawktuah = pygame.image.load(os.path.join("assets", "hawktuah.webp")).convert_alpha()

NUM_RAYS = 20  # Number of LiDAR rays
FOV = 360  # Field of view in degrees (360 for full circle)
MAX_RANGE = 200  # Max range of LiDAR in pixels
LIDAR_ANGLE_STEP = FOV / NUM_RAYS  # Angular increment per ray

tracks = [os.path.join("assets", "track1.png"), (420, 512), (413, 130)]
track = pygame.image.load(tracks[0]).convert()
car_img = pygame.image.load(os.path.join("assets", "yellow-car-top-view-free-png.png")).convert_alpha()  # Smaller car to represent RC car

def eval_genomes(genomes, config):
    num = 0
    for genome_id, genome in genomes:
        num2 = 0
        num+=1
        net = neat.nn.FeedForwardNetwork.create(genome, config) 
        car = Car(WIDTH, HEIGHT, tracks[1], car_img, tracks[2])
        lidar = Lidar(track, WIDTH, HEIGHT)
        running = True
        start = time.time()
        while running:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            x, y, angle = car.report_position()
            if num2 == 0:
                distances, hit_points = lidar.simulate_lidar(x, y, -angle)
                normalized_distances = [d / MAX_RANGE for d in distances]
                output = net.activate(normalized_distances)
                steering = output[0]
                throttle = output[1]    
                car.handling(throttle)
                car.change_velocity()
                car.steering(steering)
            
            check_if_hit, _ = lidar.simulate_lidar(x, y, -angle)
            for distance in check_if_hit:  
                if distance <= 0:
                    running = False
            if not car.is_moving(start):
                running = False

            genome.fitness = car.get_distance_covered() / 1000.0
            rotated_car, rotated_rect = car.moving_car()
            screen.blit(track, (0, 0))
            screen.blit(rotated_car, rotated_rect.topleft)
            for hit_point in hit_points:
                if hit_points.index(hit_point) == 4 or hit_points.index(hit_point) == 12:
                
                    pygame.draw.line(screen, (0, 255, 0), (x, y), hit_point)
                else:
                    pygame.draw.line(screen, (255, 0, 0), (x, y), hit_point)
            
            if car.has_finished():
                genome.fitness += 5
                running = False
            # Update display
            #text_surface = my_font.render(str(round(x)) + "," + str(round(y)), False, (0, 0, 0))
            #screen.blit(text_surface, (0,100))
            text_surface = my_font.render(str(num), False, (0, 0, 0))
            screen.blit(text_surface, (0,0))
            fps_surface = my_font.render(str(round(clock.get_fps())), False, (0, 0, 0))
            screen.blit(fps_surface, (0,50))
            fps_surface = my_font.render(str(round(car.get_velocity())), False, (0, 0, 0))
            screen.blit(fps_surface, (0,100))
            fps_surface = my_font.render(str(time.time() - start), False, (0, 0, 0))
            screen.blit(fps_surface, (100,0))
            pygame.display.flip()
            num2 += 1
            if num2 == 11:
                num2 = 0
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
    population.add_reporter(neat.Checkpointer(generation_interval=5, filename_prefix='neat-checkpoint'))


    # Run for up to 50 generations
    winner = population.run(eval_genomes, 1)
    with open(os.path.join("neat", "best_genome.pkl"), 'wb') as f:
        pickle.dump(winner, f)
    # Display the winning genome
    print('\nBest genome:\n{!s}'.format(winner))
    pygame.quit()
    visualize.draw_net(config, winner, True) # plot best neural network
    visualize.plot_stats(stats, ylog=False, view=True) # plot average/best fitness'

if __name__ == "__main__":
    config_path = os.path.join("neat", "config-feedforward.txt")  # Path to your NEAT config file
    checkpoint_file = None
    run_neat(config_path, checkpoint_file)
    pygame.quit()

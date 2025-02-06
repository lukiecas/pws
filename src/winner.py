import neat
import pickle
import pygame
import time
from car import Car
from lidar_sensor import Lidar
import os
import matplotlib.pyplot as plt


os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

MAX_RANGE = 800

tracks = [os.path.join("assets", "track2.png"), (420, 520), (420, 130)]
track = pygame.image.load(tracks[0]).convert()
car_img = pygame.image.load(os.path.join("assets", "yellow-car-top-view-free-png.png")).convert_alpha()  # Smaller car to represent RC car

config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "/home/sjanschen/localpws/neat/config-feedforward.txt"
    )

with open('/home/sjanschen/2pws/pws/neat/model_v4.pkl', 'rb') as f:
    winner = pickle.load(f)
net = neat.nn.FeedForwardNetwork.create(winner, config)
car = Car(WIDTH, HEIGHT, tracks[1], car_img, tracks[2])
lidar = Lidar(track, WIDTH, HEIGHT)
running = True
start = time.time()
num2 = 0
ti = []
tr = []
st = []
import random
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    x, y, angle = car.report_position()
    distances, hit_points = lidar.simulate_lidar(x, y, -angle)
    distances[12] = 0

    normalized_distances = [d / (MAX_RANGE) for d in distances]
    output = net.activate(normalized_distances)
    steering = output[0]
    throttle = output[1]  
    print(normalized_distances)
    car.handling(throttle)
    car.steering(steering)
    car.change_velocity()
    tr.append(normalized_distances[0])
    ti.append(car.get_distance_covered())
    st.append(steering)
    check_if_hit, _ = lidar.simulate_lidar(x, y, -angle)
    for distance in check_if_hit:  
        if distance <= 0:
            running = False
            print(distance)
    # if not car.is_moving(start):
    #     running = False

    rotated_car, rotated_rect = car.moving_car()
    screen.blit(track, (0, 0))
    screen.blit(rotated_car, rotated_rect.topleft)
    for hit_point in hit_points:
        if hit_points.index(hit_point) == 0:
            pygame.draw.line(screen, (0, 255, 0), (x, y), hit_point)
        elif hit_points.index(hit_point) == 8:
            pygame.draw.line(screen, (0, 255, 0), (x, y), hit_point)
        else:
            pygame.draw.line(screen, (255, 0, 0), (x, y), hit_point)
    
    # if car.has_finished():
    #     running = False
    # Update display
    #text_surface = my_font.render(str(round(x)) + "," + str(round(y)), False, (0, 0, 0))
    #screen.blit(text_surface, (0,100))
    fps_surface = my_font.render(str(round(clock.get_fps())), False, (0, 0, 0))
    screen.blit(fps_surface, (0,50))
    fps_surface = my_font.render(str(round(car.get_velocity())), False, (0, 0, 0))
    screen.blit(fps_surface, (0,100))
    fps_surface = my_font.render(str(time.time() - start), False, (0, 0, 0))
    screen.blit(fps_surface, (100,0))
    fps_surface = my_font.render(str(num2), False, (0, 0, 0))
    screen.blit(fps_surface, (200,100))
    pygame.display.flip()
    
    # Frame rate
    clock.tick(5000)

plt.plot(ti, st, label="stuur")
plt.plot(ti, tr, label="gas")
plt.legend(loc="upper right")
plt.show()
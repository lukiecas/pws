import pygame
import random
import neat
import math
import numpy as np
pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
car_img = pygame.image.load("C:\\Users\\lucas\\Desktop\\pws\\pws\\pws-main\\yellow-car-top-view-free-png.png").convert_alpha()  # Smaller car to represent RC car
car_img = pygame.transform.scale(car_img, (30, 20))
car_rect = car_img.get_rect(center=(WIDTH//2, HEIGHT//2))  # Car's starting position

NUM_RAYS = 20  # Number of LiDAR rays
FOV = 360  # Field of view in degrees (360 for full circle)
MAX_RANGE = 200  # Max range of LiDAR in pixels
LIDAR_ANGLE_STEP = FOV / NUM_RAYS  # Angular increment per ray

# Physics variables
x, y = WIDTH // 2, HEIGHT // 2  # Initial position
velocity = 0  # Initial velocity
angle = 0  # Initial orientation (angle in radians)
angular_velocity = 0  # Initial angular velocity
acceleration = 0  # Acceleration
steering_angle = 0  # Steering input

# Constants for RC car behavior
MAX_VELOCITY = 8  # Max speed is higher for an RC car
ACCELERATION_RATE = 0.2  # RC cars accelerate faster
BRAKE_RATE = 0.1  # RC cars decelerate faster
MAX_STEERING_ANGLE = 70  # RC cars can turn more sharply
TURN_RATE = 8  # Faster turn rate
FRICTION = 0.95  # Reduced friction to simulate more skidding

# Car dimensions
car_length = 30  # Smaller car length
def eval_genomes(genomes, config):
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
            
        genome.fitness = fitness
def run_neat():
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
    print(f"Best genome: {winner}")
tracks = {"1" : ["track1.png", (420, 512)],}
track = pygame.image.load(tracks["1"][0]).convert()
x, y = tracks["1"][1]
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
    if keys[pygame.K_UP]:
        acceleration = ACCELERATION_RATE
    elif keys[pygame.K_DOWN]:
        acceleration = -BRAKE_RATE
    else:
        acceleration = 0
    
    if keys[pygame.K_LEFT]:
        steering_angle = min(steering_angle + 2, MAX_STEERING_ANGLE)
    elif keys[pygame.K_RIGHT]:
        steering_angle = max(steering_angle - 2, -MAX_STEERING_ANGLE)
    else:
        steering_angle *= 0.9  # Return steering gradually to center
    
    # Update physics for RC car
    velocity += acceleration
    velocity = max(min(velocity, MAX_VELOCITY), -MAX_VELOCITY)  # Clamp velocity
    
    # Apply friction to velocity
    velocity *= FRICTION
    
    # If there's velocity, calculate the turning radius
    if velocity != 0 and steering_angle != 0:
        turning_radius = car_length / math.sin(math.radians(abs(steering_angle)))
        angular_velocity = velocity / turning_radius
        
        # Update angle based on steering and velocity
        if steering_angle < 0:
            angle -= math.degrees(angular_velocity) * (velocity / MAX_VELOCITY)
        else:
            angle += math.degrees(angular_velocity) * (velocity / MAX_VELOCITY)
    else:
        angular_velocity = 0
    distances, hit_points = simulate_lidar(x, y)
    # Calculate new position
    x += velocity * math.cos(math.radians(angle))
    y -= velocity * math.sin(math.radians(angle))  # Y-axis is inverted in Pygame
    for distance in distances:  
        if distance <= 0:
            x, y = tracks["1"][1]
    # Update car rect position
    for distance in distances:
        print(distance)
    car_rect.center = (x, y)
    
    # Rotate car image
    rotated_car = pygame.transform.rotate(car_img, angle)  # Pygame uses clockwise rotation
    rotated_rect = rotated_car.get_rect(center=car_rect.center)
    
    # Draw car
    screen.blit(track, (0, 0))
    screen.blit(rotated_car, rotated_rect.topleft)
    
    # Update display
    pygame.display.flip()
    
    # Frame rate
    clock.tick(60)

pygame.quit()
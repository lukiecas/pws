import pygame
import math
class Car:
    def __init__(self, WIDTH, HEIGHT, track_init):
        car_img = pygame.image.load("C:\\Users\\lucas\\Desktop\\pws\\pws\\pws-main\\yellow-car-top-view-free-png.png").convert_alpha()  # Smaller car to represent RC car
        self.car_img = pygame.transform.scale(car_img, (30, 20))
        self.car_rect = car_img.get_rect(center=(WIDTH//2, HEIGHT//2))  # Car's starting position
        # Constants for RC car behavior
        self.MAX_VELOCITY = 8  # Max speed is higher for an RC car
        self.ACCELERATION_RATE = 0.2  # RC cars accelerate faster
        self.BRAKE_RATE = 0.1  # RC cars decelerate faster
        self.MAX_STEERING_ANGLE = 70  # RC cars can turn more sharply
        self.TURN_RATE = 8  # Faster turn rate
        self.FRICTION = 0.95  # Reduced friction to simulate more skidding
        self.velocity = 0  # Initial velocity
        self.angle = 0  # Initial orientation (angle in radians)
        self.angular_velocity = 0  # Initial angular velocity
        self.acceleration = 0  # Acceleration
        self.steering_angle = 0  # Steering input
        self.car_length = 30
        self.track_init = track_init
        self.x, self.y = track_init  # Initial position
    def key_pressed(self, keys):
        self.keys = keys
    def steering(self):
        if self.keys[pygame.K_LEFT]:
            self.steering_angle = min(self.steering_angle + 2, self.MAX_STEERING_ANGLE)
            print("steering left")
        elif self.keys[pygame.K_RIGHT]:
            self.steering_angle = max(self.steering_angle - 2, -self.MAX_STEERING_ANGLE)
            print("steering right")
        else:
            self.steering_angle *= 0.9  # Return steering gradually to center
    def handling(self):
        if self.keys[pygame.K_UP]:
            self.acceleration = self.ACCELERATION_RATE
        elif self.keys[pygame.K_DOWN]:
            self.acceleration = -self.BRAKE_RATE
        else:
            self.acceleration = 0
    def change_velocity(self):
        self.velocity += self.acceleration
        self.velocity = max(min(self.velocity, self.MAX_VELOCITY), -self.MAX_VELOCITY)
        self.velocity *= self.FRICTION
    def moving_car(self):
        # If there's velocity, calculate the turning radius
        if self.velocity != 0 and self.steering_angle != 0:
            turning_radius = self.car_length / math.sin(math.radians(abs(self.steering_angle)))
            self.angular_velocity = self.velocity / turning_radius
            
            # Update angle based on steering and velocity
            if self.steering_angle < 0:
                self.angle -= math.degrees(self.angular_velocity) * (self.velocity / self.MAX_VELOCITY)
            else:
                self.angle += math.degrees(self.angular_velocity) * (self.velocity / self.MAX_VELOCITY)
        else:
            self.angular_velocity = 0
        
        # Calculate new position
        self.x += self.velocity * math.cos(math.radians(self.angle))
        self.y -= self.velocity * math.sin(math.radians(self.angle))  # Y-axis is inverted in Pygame
        # Update car rect position
        
        self.car_rect.center = (self.x, self.y)
        # Rotate car image
        rotated_car = pygame.transform.rotate(self.car_img, self.angle)  # Pygame uses clockwise rotation
        rotated_rect = rotated_car.get_rect(center=self.car_rect.center)
        return rotated_car, rotated_rect
    def report_position(self):
        return self.x, self.y
    def has_died(self):
        self.x, self.y = self.track_init
    def has_finished(self):
        if self.x == self.track_init[0] and self.y > self.track_init[1] + 50:
            return True
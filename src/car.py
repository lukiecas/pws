import pygame
import math
import time
class Car:
    def __init__(self, WIDTH, HEIGHT, track_init, car_img, checkpoint):
        self.checkpoint = checkpoint
        self.car_img = pygame.transform.scale(car_img, (30, 20))
        self.car_rect = car_img.get_rect(center=(WIDTH//2, HEIGHT//2))  # Car's starting position
        # Constants for RC car behavior
        self.MAX_VELOCITY = 8  # Max speed is higher for an RC car
        self.ACCELERATION_RATE = 0.2  # RC cars accelerate faster
        self.BRAKE_RATE = 0.1  # RC cars decelerate faster
          # RC cars can turn more sharply
        self.TURN_RATE = 8  # Faster turn rate
        self.FRICTION = 0.95  # Reduced friction to simulate more skidding
        self.velocity = 0  # Initial velocity
        self.angle = 0  # Initial orientation (angle in radians)
        self.angular_velocity = 0  # Initial angular velocity
        self.acceleration = 0  # Acceleration
        self.steering_angle = 0  # Steering input
        self.car_length = 30
        self.distance_covered = 0
        self.track_init = track_init
        self.checkpoint_reached = False
        self.x, self.y = track_init  # Initial position
    def steering(self, max_steering_angle):
        self.max_steering_angle = max_steering_angle
        
        if max_steering_angle > 0:
            self.steering_angle = min(self.steering_angle + 2, self.max_steering_angle * 70)
        
        elif max_steering_angle < 0:
            self.steering_angle = max(self.steering_angle - 2, self.max_steering_angle * 70)
            
        else:
            self.steering_angle *= 0.9  # Return steering gradually to center
    def handling(self, throttle):
        self.throttle = throttle
        if self.throttle > 0: 
            self.acceleration = self.throttle * 0.2
        elif self.throttle < 0:
            self.acceleration = self.throttle * 0.1
        else:
            self.acceleration = 0
    def change_velocity(self):
        self.velocity += self.acceleration
        self.velocity = max(min(self.velocity, self.throttle * self.MAX_VELOCITY), 0)
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
        return self.x, self.y, self.angle
    def get_velocity(self):
        return self.velocity
    def is_moving(self, start_time):
        if self.velocity == 0 and (time.time() - start_time) >= 1:
            return False
        else:
            return True
    def reached_checkpoint(self):
        if ((self.checkpoint[0] - 20)< self.x < (self.checkpoint[0] + 20) and self.y < self.checkpoint[1] + 200):
            self.checkpoint_reached = True
    def has_finished(self):
        self.reached_checkpoint()
        if  (self.track_init[0] - 20)< self.x < (self.track_init[0] + 20) and self.y > self.track_init[1] - 200 and self.checkpoint_reached:
            return True
        else:
            return False
    def get_distance_covered(self):
        self.distance_covered = self.distance_covered + self.velocity
        return self.distance_covered
    

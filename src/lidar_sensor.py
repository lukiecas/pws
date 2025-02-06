import math

class Lidar:
    def __init__(self, track, WIDTH, HEIGHT):
        self.NUM_RAYS = 16  # Number of LiDAR rays
        self.FOV = 180  # Change to 180 degrees for forward scanning
        self.MAX_RANGE = 800  # Max range of LiDAR in pixels
        self.LIDAR_ANGLE_STEP = self.FOV / (self.NUM_RAYS - 1)  # Angular increment per ray
        self.track = track
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def cast_ray(self, x, y, angle):
        for i in range(self.MAX_RANGE):
            ray_x = int(x + i * math.cos(angle))
            ray_y = int(y + i * math.sin(angle))
            
            # Check if the ray is out of bounds
            if ray_x < 0 or ray_x >= self.WIDTH or ray_y < 0 or ray_y >= self.HEIGHT:
                return (ray_x, ray_y), i
            
            # Check if the ray hits a black pixel on the track
            if self.track.get_at((ray_x, ray_y)) == (255, 255, 255, 255):  # Black pixel (track)
                return (ray_x, ray_y), i
        
        # If no collision, return the maximum range
        return (int(x + self.MAX_RANGE * math.cos(angle)), int(y + self.MAX_RANGE * math.sin(angle))), self.MAX_RANGE

    def simulate_lidar(self, x, y, car_orientation):
        distances = []
        rays = []
        
        for i in range(self.NUM_RAYS):
            # Angle spans from -90° to +90° relative to the car
            angle = math.radians(car_orientation) + math.radians(-90 + i * self.LIDAR_ANGLE_STEP)  
            hit_point, distance = self.cast_ray(x, y, angle)
            distances.append(distance)
            rays.append(hit_point)

        return distances, rays

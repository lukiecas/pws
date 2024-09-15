import math
class Lidar:
    def __init__(self, track, WIDTH, HEIGHT):
        self.NUM_RAYS = 20  # Number of LiDAR rays
        self.FOV = 360  # Field of view in degrees (360 for full circle)
        self.MAX_RANGE = 200  # Max range of LiDAR in pixels
        self.LIDAR_ANGLE_STEP = self.FOV / self.NUM_RAYS  # Angular increment per ray
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
    def simulate_lidar(self, x, y):
        distances = []
        rays = []
        
        for i in range(self.NUM_RAYS):
            angle = math.radians(i * self.LIDAR_ANGLE_STEP)  # Convert angle to radians
            hit_point, distance = self.cast_ray(x, y, angle)
            distances.append(distance)
            rays.append(hit_point)
        
        return distances, rays
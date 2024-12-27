import ydlidar
import neat
import pickle
import RPi.GPIO as GPIO
from time import sleep
# TODO: aansluiten met NEAT model

ydlidar.os_init()
ports = ydlidar.lidarPortList()
port = "/dev/ydlidar"
for key, value in ports.items():
    port = value
laser = ydlidar.CYdLidar()
laser.setlidaropt(ydlidar.LidarPropSerialPort, port)
laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 115200)
laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TRIANGLE)
laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL)
laser.setlidaropt(ydlidar.LidarPropScanFrequency, 8.0)
laser.setlidaropt(ydlidar.LidarPropSampleRate, 3)
laser.setlidaropt(ydlidar.LidarPropSingleChannel, True)
laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0)
laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0)
laser.setlidaropt(ydlidar.LidarPropMaxRange, 8.0)
laser.setlidaropt(ydlidar.LidarPropMinRange, 0.1)
laser.setlidaropt(ydlidar.LidarPropIntenstiy, False)

servo_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz
pwm.start(0)
MAX_LIDAR_RANGE = 8.0

config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        "/home/lucas/pws/neat/config-feedforward.txt"
    )

with open('/home/lucas/pws/neat/best_genome.pkl', 'rb') as f:
    winner = pickle.load(f)
net = neat.nn.FeedForwardNetwork.create(winner, config)



def set_speed(speed):
    """Set speed for continuous rotation servo."""
    # Map speed (-100 to 100) to duty cycle (1.0 to 2.0 ms)
    duty = 1.5 + (speed / 100.0) * 0.5  # 1.0ms = full reverse, 2.0ms = full forward
    pwm.ChangeDutyCycle(duty / 20 * 100)  # Convert to duty cycle percentage

def set_angle(angle, speed=1):
    """Set the servo to a specific angle gradually."""
    duty = 2 + (angle / 18)  # Convert angle to duty cycle (2-12%)
    current_duty = 2  # Assume initial position at 0 degrees
    
    if current_duty < duty:
        step = 0.1  # Increment duty cycle slowly
    else:
        step = -0.1  # Decrement duty cycle slowly

    while abs(current_duty - duty) > 0.1:  # Gradually adjust to the target
        current_duty += step
        pwm.ChangeDutyCycle(current_duty)
        sleep(speed / 100.0)  # Adjust speed (smaller is faster)

    pwm.ChangeDutyCycle(0)  # Stop sending signal after movement

def scan():
    ret = laser.initialize()
    if ret:
        ret = laser.turnOn()
        scan = ydlidar.LaserScan()
        while ret and ydlidar.os_isOk() :
            r = laser.doProcessSimple(scan)
            if r:
                desired_points = [-3.141592653589793, -2.748893571891069, -2.356194490192345, -1.9634954084936207, -1.5707963267948966, -1.1780972450961724, -0.7853981633974483, -0.39269908169872414, 0.0, 0.39269908169872414, 0.7853981633974483, 1.1780972450961724, 1.5707963267948966, 1.9634954084936207, 2.356194490192345, 2.748893571891069] # desired angles for the ML model
                data_points = []
                input_points = []
                for point in scan.points:
                    data_point = []
                    data_point.append(point.angle)
                    data_point.append(point.range)
                    data_points.append(data_point)
                angles = [data_point[0] for data_point in data_points]
                for i in desired_points:
                    closest_angle = min(angles, key=lambda x:abs(x-i))
                    index = angles.index(closest_angle)
                    input_point = data_points[index]
                    input_points.append(input_point) # dit zijn alle 16 "rays" met hoek en afstand, voer dit in de ML model
            
                # activeer hier NEAT 
                normalized_distances = [input_point[1] / MAX_LIDAR_RANGE for input_point in input_points]
                output = net.activate(normalized_distances)
                steering = output[0]
                acceleration = output[1]
                set_speed(acceleration * 100)
                set_angle(steering *180)
                print(steering)
                print(acceleration)

        laser.turnOff()
    laser.disconnecting()
pwm.stop()
GPIO.cleanup()

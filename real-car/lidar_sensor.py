import ydlidar

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
laser.setlidaropt(ydlidar.LidarPropMaxRange, 16.0)
laser.setlidaropt(ydlidar.LidarPropMinRange, 0.08)
laser.setlidaropt(ydlidar.LidarPropIntenstiy, False)

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
                    data_point.append(point.intensity)
                    data_points.append(data_point)
                angles = [data_point[0] for data_point in data_points]
                for i in desired_points:
                    closest_angle = min(angles, key=lambda x:abs(x-i))
                    index = angles.index(closest_angle)
                    input_point = data_points[index]
                    input_points.append(input_point)
            
        laser.turnOff()
    laser.disconnecting()


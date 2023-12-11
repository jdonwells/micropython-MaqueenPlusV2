# micropython-MaqueenPlusV2
A set of functions to control the DFRobot Maqueen Plus V2 robot with a micro:bit control using python.microbit.org. Put the maqueenplusv2.py file in your project by clicking Open... select the file. At the Change files? prompt select the file icon then select Add file maqueenplusv2.py. This last thing is important because otherwise, the default is to throw away the code in main.py.

imports:
from microbit import *
from maqueenplusv2 import *

first line of code:
init_maqueen()


init_maqueen() shows the robots version and adjusts the IR line sensors for diferences between version 2.0 and 2.1. 

Stop() will stop both motors.
drive(speed) will drive theoretically straight.
backup(speed) will drive backwards.
spin_left(speed) spins the robot.
spin_right(speed) also spins the robot.
motors(left speed, left direction, right speed, right direction) starts the motors running speed can be 0-255, directions can be FORWARD or BACKWARD.

read_all_line_sensors() returns an array with 5 analog readings from the 5 IR line sensors. Left rear, left, middle, right, right rear.
read_line_sensor(sensor) returns a single analog reading from the sensor chosen. Sensor can be L2, L1, M, R1, R2.

rangefinder() returns the ultrasonic rangefinder distance in centimeters.

set_servo_angle(servo, angle) sets the servo to that angle. Servo can be SERVO_1, SERVO_2, or SERVO_3. Angle is usually 0 to 180 for DFRobot tools.

set_underglow(color) sets all 4 underglow lights to the color. Color is a 6 digit hex value like 0xFF0000 would be red.
set_underglow(light, color) sets a single LED light. Light can be 0 to 3. Color is as above.
underglow_off() sets all 4 underglow lights to off.


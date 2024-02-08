from microbit import i2c
from microbit import pin8, pin12, pin13, pin14
from machine import time_pulse_us
from time import sleep_us, sleep_ms, sleep as sleep_s
from micropython import const
from microbit import *

# i2c bus location on the micro:bit.
# NAME_I2C_ADDR are adresses for robot components on the i2c bus.
I2C_ADDR = const(0x10)

# motor rotation
FORWARD = const(2)
BACKWARD = const(1)
# General purpose left right for motors and LEDs
LEFT = const(1)
RIGHT = const(2)
BOTH = const(3)

# IR line sensor constants
LEFT_IR_PIN = pin13
RIGHT_IR_PIN = pin14

# Ultrasonic Rangefinder constants
US_TRIGGER = pin8
US_ECHO = pin12
MIN_DISTANCE = const(2)  # centimeters
MAX_DISTANCE = const(450)  # centimeters
MAX_DURATION = const(38000)  # microseconds
SPEED_OF_SOUND = 343.4 * 100 / 1000000  # centemeters/microsecond

# LED constants
LEFT_LED_I2C_ADDR = const(0x04)
RIGHT_LED_I2C_ADDR = const(0x08)

# color constants
RED = const(0xFF0000)
ORANGE = const(0xFFA500)
YELLOW = const(0xFFFF00)
GREEN = const(0x00FF00)
BLUE = const(0x0000FF)
INDIGO = const(0x4B0082)
VIOLET = const(0x8A2BE2)
PURPLE = const(0xFF00FF)
WHITE = const(0xFF9070)
OFF = const(0x000000)


def I2C_send(byte0, byte1, byte2, byte3=0):
    "send 4 bytes to I2C bus"
    buffer = bytearray(4)
    buffer[0] = byte0
    buffer[1] = byte1
    buffer[2] = byte2
    buffer[3] = byte3
    i2c.write(I2C_ADDR, buffer)


# Motor functions
def stop():
    "Stop the robot's motors"
    drive(0)


def drive(speed):
    "Drive forward at speed 0-255"
    motors(speed, FORWARD, speed, FORWARD)


def backup(speed):
    "Drive backwards at speed 0-255"
    motors(speed, BACKWARD, speed, BACKWARD)


def spin_left(speed):
    "Spin the robot left at speed 0-255"
    motors(speed, BACKWARD, speed, FORWARD)


def spin_right(speed):
    "Spin the robot right at speed 0-255"
    motors(speed, FORWARD, speed, BACKWARD)


def motors(l_speed, l_direction, r_speed, r_direction):
    "Set both motor speeds 0-255 and directions (FORWARD, BACKWARD) left then right."
    _motor(LEFT, l_speed, l_direction)
    _motor(RIGHT, r_speed, r_direction)


def _motor(motor, speed, direction):
    "Set one motor (LEFT, RIGHT) speed 0-255 and direction (FORWARD, BACKWARD)"
    # cutebot speed is 0 - 100
    cutebot_speed = min(max(int(speed / 255 * 100), 0), 100)
    I2C_send(motor, direction, cutebot_speed)


# IR line sensor functions
def sensor_on_line(sensor):
    "True if IR sensor is on a line, False on white paper"
    if sensor == LEFT:
        return not bool(LEFT_IR_PIN.read_digital())
    elif sensor == RIGHT:
        return not bool(RIGHT_IR_PIN.read_digital())
    else:
        panic(1)


# Ultrasonic Rangefinder function
def rangefinder():
    "Return a range in centimeters from 2 to 450."
    US_TRIGGER.write_digital(0)
    sleep_us(2)
    US_TRIGGER.write_digital(1)
    sleep_us(10)  # we need trigger pin high for at least 10 microseconds
    US_TRIGGER.write_digital(0)
    pulse_length = time_pulse_us(US_ECHO, 1)
    if pulse_length >= MAX_DURATION:
        return MAX_DISTANCE  # out of range
    return int(pulse_length * SPEED_OF_SOUND / 2)  # round trip distance so divide by 2


# LED head light functions
def color_to_rgb(color):
    r = color >> 16
    g = color >> 8 & 0xFF
    b = color & 0xFF
    return r, g, b


def headlights(light, color):
    "Turn the LEFT, RIGHT, or BOTH headlights to some color RED, BLUE, etc. or OFF."
    if light != RIGHT:
        I2C_send(LEFT_LED_I2C_ADDR, *color_to_rgb(color))
    if light != LEFT:
        I2C_send(RIGHT_LED_I2C_ADDR, *color_to_rgb(color))


    

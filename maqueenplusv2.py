from microbit import i2c
from micropython import const
from microbit import pin13, pin14, pin15
from machine import time_pulse_us
from time import sleep_us, sleep_ms, sleep as sleep_s
from neopixel import *
from microbit import *

# i2c bus location on the micro:bit.
# NAME_I2C_ADDR are adresses for robot components on the i2c bus.
I2C_ADDR = const(0x10)

# robot version length and location
VERSION_COUNT_I2C_ADDR = const(0x32)
VERSION_DATA_I2C_ADDR = const(0x33)

# Motor constants
LEFT_MOTOR_I2C_ADDR = const(0x00)
# RIGHT_MOTOR_I2C_ADDR = 0x02 not used. I always set both.

AXLE_WIDTH = 0.095

FORWARD = const(0)
BACKWARD = const(1)

# IR sensor constants for version 2.1
LINE_SENSOR_I2C_ADDR = const(0x1D)
ANALOG_R2_I2C_ADDR = const(0x1E)
ANALOG_R1_I2C_ADDR = const(0x20)
ANALOG_M_I2C_ADDR = const(0x22)
ANALOG_L1_I2C_ADDR = const(0x24)
ANALOG_L2_I2C_ADDR = const(0x26)
ALL_ANALOG_SENSOR_I2C_ADDRS = [
    ANALOG_L2_I2C_ADDR,
    ANALOG_L1_I2C_ADDR,
    ANALOG_M_I2C_ADDR,
    ANALOG_R1_I2C_ADDR,
    ANALOG_R2_I2C_ADDR,
]

sensor_index = [0, 1, 2, 3, 4]

R2 = const(0)
R1 = const(1)
M = const(2)
L1 = const(3)
L2 = const(4)

# Ultrasonic Rangefinder constants
US_TRIGGER = pin13
US_ECHO = pin14
MIN_DISTANCE = const(2)  # centimeters
MAX_DISTANCE = const(450)  # centimeters
MAX_DURATION = const(38000)  # microseconds
SPEED_OF_SOUND = 343.4 * 100 / 1000000  # centemeters/microsecond

# LED constants
LEFT_LED_I2C_ADDR = const(0x0B)
RIGHT_LED_I2C_ADDR = const(0x0C)
LEFT = const(0)
RIGHT = const(1)
BOTH = const(2)
ON = const(1)
OFF = const(0)

# Servos
SERVO_1 = const(0x14)
SERVO_2 = const(0x15)
SERVO_3 = const(0x16)

# NeoPixel constatnts
NEO_PIXEL_PIN = pin15
RED = const(0xFF0000)
ORANGE = const(0xFFA500)
YELLOW = const(0xFFFF00)
GREEN = const(0x00FF00)
BLUE = const(0x0000FF)
INDIGO = const(0x4B0082)
VIOLET = const(0x8A2BE2)
PURPLE = const(0xFF00FF)
WHITE = const(0xFF9070)
# OFF = const(0x000000) use the other OFF zero is zero


# General purpose functions
def init_maqueen():
    global sensor_index
    display.show(Image("90009:" "09090:" "00900:" "09090:" "90009"))
    version = maqueen_version()
    display.scroll(version[-3:])
    if version[-3:] == "2.0":
        sensor_index = [4, 3, 2, 1, 0]
    elif version[-3:] == "2.1":
        pass
    display.show(Image("00009:" "00090:" "90900:" "09000:" "00000"))
    sleep_s(1)
    display.clear()


def only8bits(n):
    return max(min(n, 255), 0)


def oneBit(n):
    return n % 2


def maqueen_version():
    "Return the Maqueen board version as a string. The last 3 characters are the version."
    i2c.write(I2C_ADDR, bytes([VERSION_COUNT_I2C_ADDR]))
    count = int.from_bytes(i2c.read(I2C_ADDR, 1), "big")
    i2c.write(I2C_ADDR, bytes([VERSION_DATA_I2C_ADDR]))
    version = i2c.read(I2C_ADDR, count).decode("ascii")
    return version


def color_to_rgb(color):
    r = color >> 16
    g = color >> 8 & 0xFF
    b = color & 0xFF
    return r, g, b


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
    buf = bytearray(5)
    buf[0] = LEFT_MOTOR_I2C_ADDR
    buf[1] = oneBit(l_direction)
    buf[2] = only8bits(l_speed)
    buf[3] = oneBit(r_direction)
    buf[4] = only8bits(r_speed)
    i2c.write(I2C_ADDR, buf)


# IR line sensor functions
def read_all_line_sensors():
    "Return an array of line sensor readings. Left to right."
    values = []
    for index in sensor_index:
        i2c.write(I2C_ADDR, bytearray([ALL_ANALOG_SENSOR_I2C_ADDRS[index]]))
        buffer = i2c.read(I2C_ADDR, 2)
        values.append(buffer[1] << 8 | buffer[0])
    return values


def read_line_sensor(sensor):
    "Return a line sensor reading. On a line is about 240. Off line is about 70."
    i2c.write(I2C_ADDR, bytearray([ALL_ANALOG_SENSOR_I2C_ADDRS[sensor_index[sensor]]]))
    buffer = i2c.read(I2C_ADDR, 2)
    return buffer[1] << 8 | buffer[0]


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
def headlights(select, state):
    "Turn on or off the two front headlights. LEFT, RIGHT, or BOTH."
    if select == LEFT:
        i2c.write(I2C_ADDR, bytearray([LEFT_LED_I2C_ADDR, state]))
    elif select == RIGHT:
        i2c.write(I2C_ADDR, bytearray([RIGHT_LED_I2C_ADDR, state]))
    else:
        i2c.write(I2C_ADDR, bytearray([LEFT_LED_I2C_ADDR, state, state]))


# Servo functions
def set_servo_angle(servo, angle):
    "Set a servo to a specific angle."
    i2c.write(I2C_ADDR, bytes([servo, angle]))


# Underglow lighting functions
neo_pixel = NeoPixel(pin15, 4)


def set_underglow(color):
    rgb = color_to_rgb(color)
    for i in range(4):
        neo_pixel[i] = rgb
    neo_pixel.show()


def underglow_off():
    set_underglow(OFF)


def set_underglow_light(light, color):
    neo_pixel[light] = color_to_rgb(color)
    neo_pixel.show()

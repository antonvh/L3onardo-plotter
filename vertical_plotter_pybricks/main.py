#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
from time import sleep_ms

# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

# Settings
L_ROPE_0 = 51
R_ROPE_0 = 79
ATT_DIST = 90
CM_TO_DEG = -160
PEN_UP_POS = 0
PEN_DOWN_POS = -90
UP = 0
DOWN = 1
UNCHANGED = -1

# Create your objects here.
ev3 = EV3Brick()
mb = Motor(Port.B)
mc = Motor(Port.C)
pen = Motor(Port.A)

# Write your program here.
ev3.speaker.beep()

def triangle_area(a, b, c):
    """
    Calculate the area of a triangle by the lengths of it's sides using Heron's formula

    :param a: Length of side a
    :param b: Length of side b
    :param c: Length of side c
    :return: area (float)
    """
    half_p = (a + b + c) / 2
    return (half_p * (half_p - a) * (half_p - b) * (half_p - c)) ** 0.5

def motor_targets_from_norm_coords(x_norm, y_norm):
    x,y = normalized_to_global_coords(x_norm,y_norm)
    return motor_targets_from_coords(x,y)

def normalized_to_global_coords(x_norm, y_norm):
    # convert normalized coordinates to global coordinates in cm
    x = x_norm * CANVAS_SIZE + H_MARGIN
    y = y_norm * CANVAS_SIZE + V_MARGIN
    return x, y

def motor_targets_from_coords(x, y):
    l_rope = (x ** 2 + y ** 2) ** 0.5
    r_rope = ((ATT_DIST - x) ** 2 + y ** 2) ** 0.5
    # Compensate for changing spindle thickness.
    l_target = (l_rope - L_ROPE_0) * CM_TO_DEG - (l_rope - L_ROPE_0)**3 * 0.00303 
    r_target = (r_rope - R_ROPE_0) * CM_TO_DEG - (r_rope - R_ROPE_0)**3 * 0.00303 
    print(r_target)
    return int(l_target), int(r_target)

def move_to_norm_coord(x_norm, y_norm, pen=UNCHANGED, brake=False):
    if x_norm == -1.0:
        if y_norm == 0:
            pen_up()
        if y_norm == 1:
            pen_down()
    else:
        motor_b_target, motor_c_target = motor_targets_from_norm_coords(x_norm, y_norm)
        move_to_target((motor_b_target, motor_c_target),pen=pen, brake=brake)

def move_to_target(target, brake=False, pen=UNCHANGED, max_rate=650):
    if pen is DOWN:        # Put the pen down
        pen_down()
    elif pen is UP:      # Put the pen up
        pen_up()
    mb.run_target(max_rate, target[0], then=Stop.HOLD, wait=False)
    mc.run_target(max_rate, target[1], then=Stop.HOLD)
    while not mb.control.done():
        sleep_ms(5)

def pen_down():
    pen.run_target(200, PEN_DOWN_POS)

def pen_up():
    pen.run_target(200, PEN_UP_POS)

V_MARGIN = triangle_area(L_ROPE_0, R_ROPE_0, ATT_DIST) / ATT_DIST * 2
# Using pythagoras to find distance from bottom triangle point to left doorframe
H_MARGIN = (L_ROPE_0 ** 2 - V_MARGIN ** 2) ** 0.5
# For convenience, the canvas is square and centered between the attachment points
CANVAS_SIZE = ATT_DIST - 2 * H_MARGIN

print("postion the robot at 0,0")
while not Button.CENTER in ev3.buttons.pressed():
    if Button.UP in ev3.buttons.pressed():
        mb.run(600)
    elif Button.LEFT in ev3.buttons.pressed():
        mb.run(-600)
    else:
        mb.stop()
    if Button.RIGHT in ev3.buttons.pressed():
        mc.run(600)
    elif Button.DOWN in ev3.buttons.pressed():
        mc.run(-600)
    else:
        mc.stop()

mb.reset_angle(0)
mc.reset_angle(0)


print("Loading coordinates")
pen.run_until_stalled(-100)
pen.reset_angle(PEN_DOWN_POS)
pen_up()

with open("coords.csv") as coordsfile:
    _ = coordsfile.readline()
    c = tuple([float(c) for c in coordsfile.readline().split(",")])
    move_to_norm_coord(*c)
    pen_down()
    for line in coordsfile.readlines():
        c = tuple([float(c) for c in line.split(",")])
        move_to_norm_coord(*c)
# print("Done: ",len(pointlist))
pen_up()
move_to_norm_coord(0,0)
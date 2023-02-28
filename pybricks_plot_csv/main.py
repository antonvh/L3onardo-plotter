#!/usr/bin/env pybricks-micropython

## This scripts opens a file coords.csv and plots all coordinates
## In that file using Anton's Mindstorms Vertical plotter.
__author__ = "Anton's Mindstorms"

## USAGE
# Generate a coords.csv file with the L3onardo python scripts in the
# directory above.
# Then run this script. The output is symlinked, so it will be uploaded
# Automatically.

## SETUP:
# Hang the plotter in the top and middle of the plotting area.
# Measure the length of both wires up to their attachment
# Measure the distance between the attachments
# Update the parameter in the constants of the script.

## SETTINGS
CANVAS_SIZE = 35 #cm, square
WIRE_START_LENGTH = 76 #cm
ATTACHMENT_WIDTH = 90 #cm
CSV_FILE = "coords.csv"
MAX_RATE = 600 # Max Deg/s when running to coordinates
MIN_MANEUVER_TIME = 0.15 #s
CM_TO_DEG = -160.8
NUMLINES = 300 # Coordinates to schedule in one go
SMOOTH_DELTA_V = 200 # deg/s

## CONSTANTS
PEN_UP_POS = 60
PEN_DOWN_POS = 0

UP = 0
DOWN = 1
UNCHANGED = -1
H_MARGIN = (ATTACHMENT_WIDTH - CANVAS_SIZE)/2
V_MARGIN = (WIRE_START_LENGTH**2 - (ATTACHMENT_WIDTH/2)**2)**0.5

# Imports
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.media.ev3dev import SoundFile, ImageFile
import math

# Setup devices
ev3 = EV3Brick()
pen_motor = Motor(Port.A)
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
ev3.speaker.beep()
timer = StopWatch()

pen_motor.run_until_stalled(-200, duty_limit=30)
pen_motor.reset_angle(PEN_DOWN_POS)

# drive_motors = [left_motor, right_motor]
# all_motors = [left_motor, right_motor, pen_motor]

def pen(target=UNCHANGED):
    if target == UP:
        pen_motor.run_target(400, PEN_UP_POS)
    elif target == DOWN:
        pen_motor.run_target(400, PEN_DOWN_POS)
pen(UP)

### Calculations for global (doorframe) to local (canvas) coordinates and back. ###
def normalized_to_global_coords(x_norm, y_norm):
    # convert normalized coordinates to global coordinates in cm
    x = x_norm * CANVAS_SIZE + H_MARGIN
    y = y_norm * CANVAS_SIZE + V_MARGIN
    return x, y

def motor_targets_from_norm_coords(x_norm, y_norm):
    x,y = normalized_to_global_coords(x_norm, y_norm)
    return motor_targets_from_coords(x,y)

def motor_targets_from_coords(x, y):
    l_rope = (x ** 2 + y ** 2) ** 0.5
    r_rope = ((ATTACHMENT_WIDTH - x) ** 2 + y ** 2) ** 0.5
    # Compensate for changing spindle thickness.
    l_target = (l_rope - WIRE_START_LENGTH) * CM_TO_DEG - (l_rope - WIRE_START_LENGTH)**3 * 0.00303 
    r_target = (r_rope - WIRE_START_LENGTH) * CM_TO_DEG - (r_rope - WIRE_START_LENGTH)**3 * 0.00303 
    return int(l_target), int(r_target)

def move_to_coord(x,y, pen=UNCHANGED):
    motor_b_target, motor_c_target  = motor_targets_from_coords(x, y)
    move_to_target((motor_b_target, motor_c_target), pen)

def move_to_norm_coord(x_norm, y_norm, pen=UNCHANGED):
    motor_b_target, motor_c_target = motor_targets_from_norm_coords(x_norm, y_norm)
    move_to_target((motor_b_target, motor_c_target), pen)

def interpolate(factor, start, stop, smooth=1.0):
    factor = min(max(factor,0),1)
    smooth = min(max(smooth,0),1)
    smooth_progress = -0.5*(math.cos(factor*3.1415)-1) * (stop-start)
    linear_progress = factor * (stop-start)
    return round(
        start + smooth*smooth_progress + (1-smooth)*linear_progress
    )

def move_to_targets(targets):
    # Create schedule for movements
    schedule = [0]
    inflection = [1]
    maneuver_time = 0
    targets = [(left_motor.angle(), right_motor.angle())] + targets
    
    for i in range(1, len(targets)):
        delta_l = targets[i][0]-targets[i-1][0]
        delta_r = targets[i][1]-targets[i-1][1]
        maneuver_time += max(abs(delta_l), abs(delta_r))/MAX_RATE + MIN_MANEUVER_TIME 
        schedule += [maneuver_time]

    for i in range(1, len(targets)-1):
        maneuver_time1 = schedule[i]-schedule[i-1]
        speed_l1 = (targets[i][0]-targets[i-1][0])/maneuver_time1
        speed_r1 = (targets[i][1]-targets[i-1][1])/maneuver_time1
        maneuver_time2 = schedule[i+1]-schedule[i]
        speed_l2 = (targets[i+1][0]-targets[i][0])/maneuver_time2
        speed_r2 = (targets[i+1][1]-targets[i][1])/maneuver_time2
        delta_v_l = abs((speed_l2-speed_l1)/SMOOTH_DELTA_V)
        delta_v_r = abs((speed_r2-speed_r1)/SMOOTH_DELTA_V)
        inflection += [max(delta_v_l, delta_v_r)]
    inflection += [1]

    # Execute movements according to schedule
    timer.reset()
    for i in range(1, len(schedule)):
        elapsed = timer.time()/1000
        while elapsed < schedule[i]:
            elapsed_i = elapsed - schedule[i-1]
            total_i = schedule[i] - schedule[i-1]
            progress = elapsed_i/total_i
            if progress < 0.5:
                smoothing = inflection[i-1]
            else:
                smoothing = inflection[i]

            tgt_l = interpolate(progress, targets[i-1][0], targets[i][0], smooth=smoothing)
            tgt_r = interpolate(progress, targets[i-1][1], targets[i][1], smooth=smoothing)
            left_motor.track_target(tgt_l)
            right_motor.track_target(tgt_r)

            elapsed = timer.time()/1000
    left_motor.stop()
    right_motor.stop()

def move_to_target(target, pen_target=UNCHANGED):
    pen(pen_target)

    start_l = left_motor.angle()
    start_r = right_motor.angle()
    delta_l = target[0]-start_l
    delta_r = target[1]-start_r
    total_t = int(max(abs(delta_l), abs(delta_r))/MAX_RATE * 1000)
    
    timer.reset()
    while timer.time() < total_t:
        tgt_l = interpolate(timer.time()/total_t, start_l, target[0])
        tgt_r = interpolate(timer.time()/total_t, start_r, target[1])
        left_motor.track_target(tgt_l)
        right_motor.track_target(tgt_r)

    left_motor.track_target(target[0])
    right_motor.track_target(target[1])
    wait(20)
    left_motor.stop(Stop.HOLD)
    right_motor.stop(Stop.HOLD)
    wait(20)
        
### Advanced plotting functions by chaining movement functions ###

def test_drive():
    # Drive a square to all sides of the canvas
    move_to_norm_coord(0,0)
    move_to_norm_coord(0,1)
    move_to_norm_coord(1,1)
    move_to_norm_coord(1,0)
    move_to_norm_coord(0.5,0)
    
def plot_from_file(filename='coords.csv'):
    """
    Generator function for plotting from coords.csv file. After each next() it returns the pct done of the plotting
    This way the plotting can easily be aborted and status can be given.
    Usage:

    gen = plot_from_file(myfile)
    while 1:
        try:
            pct_done = next(gen)
        except StopIteration:
            break

    :param filename: str
    :return: percentage done: float
    """
    csv_file = open(filename)

    # Get the first coordinate
    coord = [float(n) for n in csv_file.readline().split(",")]
    line_count = 0
    if len(coord) == 1:
        # length is on the first line.
        num_coords = int(coord[0])  
        # Get another coordinate
        coord = [float(n) for n in csv_file.readline().split(",")]
        line_count += 1
    if coord[0] < 0:
        # It's a pen command. Ignore this for now, and get another one.
        # We'll be driving to the first coord with pen up anyway.
        coord = [float(n) for n in csv_file.readline().split(",")]
        line_count += 1

    # Drive towards it
    pen(UP)
    move_to_norm_coord(*coord) # Allows for x,y and x,y,pen coordinates
    pen_target = DOWN
    pen(pen_target)
    pen_status = pen_target
    
    end_of_file = False
    while not end_of_file:
        targets = []
        while len(targets) < NUMLINES:
            try:
                coord = [float(n) for n in csv_file.readline().split(",")]
                line_count += 1
            except:
                # End of file
                end_of_file = True
                break

            if len(coord) >= 2 and coord[0] >= 0:
                # We have two regular coordinates
                targets += [motor_targets_from_norm_coords(coord[0], coord[1])]
            
            # When the first coordinate is -1.0 or we have three coordinates,
            # there is a pen command. 0 means up, 1 means down.
            if len(coord) == 2 and coord[0] < 0:
                pen_target = int(coord[1])
            elif len(coord) == 3:
                pen_target = int(coord[2])

            # Pen changes, time to start moving.
            if pen_target != pen_status:
                break
        
        # We have a list of motor targets, without pen changes. Let's run by them.
        move_to_targets(targets)

        # Update the pen, in case it changed.
        pen(pen_target)
        pen_status = pen_target

        # Update the generator with % done and wait for a 'go' on the next batch
        yield ( line_count / num_coords )
        
    csv_file.close()
    pen(UP)    
    move_to_norm_coord(0.5, 0)
    yield 1.00


while True:
    if Button.UP in ev3.buttons.pressed():
        left_motor.run(450)
    elif Button.LEFT in ev3.buttons.pressed():
        left_motor.run(-450)
    else:
        left_motor.stop(Stop.BRAKE)

    if Button.DOWN in ev3.buttons.pressed():
        right_motor.run(-450)
    elif Button.RIGHT in ev3.buttons.pressed():
        right_motor.run(450)
    else:
        right_motor.stop(Stop.BRAKE)

    if Button.CENTER in ev3.buttons.pressed():
        left_motor.stop(Stop.HOLD)
        right_motor.stop(Stop.HOLD)
        left_motor.reset_angle(0)
        right_motor.reset_angle(0)
        # test_drive()
        gen = plot_from_file()
        while True:
            try:
                print("{}% done".format(int(next(gen)*100)))
            except StopIteration:
                break
        ev3.speaker.beep()
        pen(UP)
        move_to_norm_coord(0.5,0)
        

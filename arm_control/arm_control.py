'''
arm_control.py

This file is for converting the logical drawing instructions (from image processing) into physical units and arm angles.
Then, it sends the physical instructions to motor_control.py to move the actual arm motors.
'''

import time
from math import *
from motor_control import MotorController, MotorCommand

# Arm segment lengths (units in mm)
L1 = 160.0 # TODO: Update limb lengths
L2 = 160.0
L3 = 50.0
ARM_MAX_LENGTH = L1 + L2
MIN_RADIUS = 100.0  # Closest to the base that the arm can reach

PEN_R_OFFSET = 10.0     # Horizontal offset from wrist of the arm to pen location
PEN_Z_OFFSET = 50.0     # Vertical offset from wrist of arm to tip of pen

GROUND_TO_CANVAS_DISTANCE = 0   # How far above the ground the canvas is
Y_REACH_MAX = 0 # init in calculate_arm_reach()
Y_REACH_MIN = 0 # init in calculate_arm_reach()

GROUND_TO_BASE_HEIGHT = 122.0 # Height from first arm joint to ground

PEN_LIFT_DISTANCE   = 10.0                              # Distance to lift pen off the canvas (mm)
PEN_DOWN_Z          = - GROUND_TO_BASE_HEIGHT      # Pen is on the canvas
PEN_UP_Z            = PEN_DOWN_Z + PEN_LIFT_DISTANCE    # unit in mm

# CANVAS_X_MM = 279.4 # units in mm
# CANVAS_Y_MM = 215.9 # units in mm

CANVAS_X_MM = 250.0 # units in mm
CANVAS_Y_MM = 187.5 # units in mm

CANVAS_X_PX = 1024
CANVAS_Y_PX = 786

PX_TO_MM_RATIO = CANVAS_Y_PX / CANVAS_Y_MM

CANVAS_TO_POLAR_OFFSET_X = -CANVAS_X_MM / 2
CANVAS_TO_POLAR_OFFSET_Y = CANVAS_Y_MM + MIN_RADIUS # Remember to invert Y; opencv increases Y downwards

ARM_SPEED_MM_PER_S = 50.0
PEN_UP_DOWN_DURATION = 0.1


class ArmController:

    def __init__(self):
        print ("Initializing ArmController...")
        self.curr_x = 0
        self.curr_y = 0
        self.curr_z = PEN_UP_Z
        self.instructions = []
        self.motor_commands = []


    # Loads instructions and image metadata from image processing
    def load_instructions(self, instructions, img_shape):
        self.instructions = instructions
        self.img_shape = img_shape
        self.img_center_offset_x = (CANVAS_X_PX - img_shape[1]) / 2
        self.img_center_offset_y = (CANVAS_Y_PX - img_shape[0]) / 2

        print ("Loaded {0} drawing instruction(s)".format(len(instructions)))


    # Processes the loaded instructions, then calls starts running the motors on a new thread
    def draw_loaded_instructions(self):

        # Convert drawing instructions into motor commands
        self.motor_commands = []
        for line in self.instructions:
            self.create_commands_for_line(line)

        # debug
        for cmd in self.motor_commands:
            print cmd.to_string()

        # Load commands into MotorController
        mc = MotorController()

        # Start draw on seperate thread, so everything else can keep running
        mc.run_motor_commands(self.motor)

        # Update status messages etc


    # Parses a line instruction into motor commands
    def create_commands_for_line(self, line):
        # Pen-up and select color
        self.pen_up()

        # Move to start of line
        self.move_to(line.points[0])

        # Move pen down to canvas
        self.pen_down()

         # Move pen to each coordinate of the line (connect-the-dots)
        for point in line.points:
            self.move_to(point)

        self.pen_up()


    # Adds command to move to canvas-coordinate, while keeping same Z
    def move_to(self, coordinate):
        # print "move_to coordinate", coordinate

        target_x = coordinate[0]
        target_y = coordinate[1]

        # Convert units to mm
        target_x_mm = px_to_mm(target_x)
        target_y_mm = px_to_mm(target_y)

        # Transform canvas coordinates into polar
        # Also tries to center the image if it doesnt fully fit resolution
        # Invert Y because openCV has y backwards
        x_polar = CANVAS_TO_POLAR_OFFSET_X + (target_x_mm + self.img_center_offset_x)
        y_polar = CANVAS_TO_POLAR_OFFSET_Y - (target_y_mm + self.img_center_offset_y)

        # Skip if already on same pixel
        if x_polar == self.curr_x and y_polar == self.curr_y:
            return

        # print("target", target_x, target_y)
        # print("target polar", x_polar, y_polar)

        # Get angle of final positions of each arm motor
        # angles = points_to_angles([[target_y_mm], [PEN_DOWN_Z]]) # obsolete
        base_angle, j1_angle, j2_angle = point_to_angles(x_polar, y_polar, self.curr_z)

        # TODO: Slice movement into smaller segments for straight lines

        # Calculate how fast to move the motors (in seconds)
        # distance_to_target = distance(self.curr_x, self.curr_y, target_x, target_y)
        # distance_to_target_mm = px_to_mm(distance_to_target)
        # move_duration = float(distance_to_target_mm) / ARM_SPEED_MM_PER_S

        # Add to motor command list
        new_command = MotorCommand(base_angle, j1_angle, j2_angle, 0, 2)
        self.motor_commands.append(new_command)

        self.curr_x = x_polar
        self.curr_y = y_polar


    def pen_up(self):

        # Skip if pen is already up
        if (self.curr_z == PEN_UP_Z):
            return

        # Get angle of final positions of each arm motor
        # Keep same x and y
        base_angle, joint_angle1, joint_angle2 = point_to_angles(self.curr_x, self.curr_y, PEN_UP_Z)
        self.curr_z = PEN_UP_Z

        # Add to motor command list
        # new_command = MotorCommand(theta1, theta2, theta3, px_to_mm(self.curr_x), 0, PEN_UP_DOWN_DURATION)
        # self.motor_commands.append(new_command)


    def pen_down(self):

        # Skip if pen is already down
        if (self.curr_z == PEN_DOWN_Z):
            return

        # Get angle of final positions of each arm motor
        # Keep same x and y
        base_angle, joint_angle1, joint_angle2 = point_to_angles(self.curr_x, self.curr_y, PEN_DOWN_Z)
        self.curr_z = PEN_DOWN_Z

        # Add to motor command list
        # new_command = MotorCommand(theta1, theta2, theta3, px_to_mm(self.curr_x), 0, PEN_UP_DOWN_DURATION)
        # self.motor_commands.append(new_command)


    def testing(self):
        # TEST - artificial progress
        time_current = 0
        while (True):
            if (time_current == 5):
                print ("drawing complete")
                return

            #pause
            if (draw_pause):
                print ("drawing paused")
                time.sleep(1)
            #unpause
            else:
                time_current += 1
                print ("drawing (" + str(time_current) + "/5)")
                time.sleep(1)

    def draw_image_pause(self):
        global draw_pause
        if (draw_pause == False):
            draw_pause = True
        else:
            draw_pause = False

    def draw_image_abort(self):
        print ("abort button not yet implemented!")
        global draw_abort
        draw_abort = True

# TEST
draw_pause = False
draw_abort = False

# end ArmController


# Function to support selecting pen colors
def select_pen_color(color):
    # Find angle of corresponding color based on map

    # Send angle to servo control
    pass


def points_to_angles_old(points):

    print "points_to_angles start:", points

    # Defining the end effector
    # z represents "depth" of the tip of the arm
    y = points[0]
    z = points[1]

    # Initialize arrays
    pos_a = [None] * len(z)
    neg_a = [None] * len(z)
    b = [None] * len(z)

    rad_Theta2 = [None] * len(z)
    Theta2_Deg = [None] * len(z)

    k1 = [None] * len(z)
    k2 = [None] * len(z)
    rad_Theta1 = [None] * len(z)
    Theta1_Deg = [None] * len(z)

    Theta3_Deg = [None] * len(z)

    for i in range(len(z)):
        # Check point is within arm's reach
        # if (distance(0, 0, y[i], z[i]) >= ARM_MAX_LENGTH):
            # print "Error: Arm cannot reach y=", y[i], "and z=", z[i]
            # continue

        # The length from origin to end effector initializtion
        sqrt_input = 1 - ( ( (z[i]**2 + y[i]**2 - L1**2 - L2**2) / (2 * L2 * L1) ) ** 2 )
        if sqrt_input < 0:
            print "Error: sqrt_input is less than 0 for y=", y[i], "and z=", z[i]
            continue

        pos_a[i] = sqrt(sqrt_input);
        neg_a[i] = -sqrt(sqrt_input);
        # pos_a[i] = sqrt(1-(((z[i]**2+y[i]**2-L1**2-L2**2)/(2*L2*L1))**2));
        # neg_a[i] = -sqrt(1 - ( ( (z[i]**2 + y[i]**2 - L1**2 - L2**2) / (2 * L2 * L1) )**2 ));
        b[i] = ((z[i]**2) + (y[i]**2) - L1**2 - L2**2) / (2 * L1 * L2);

        rad_Theta2[i] = atan2(pos_a[i], b[i]);
        Theta2_Deg[i] = degrees(rad_Theta2[i]);

        # We have calculated Theta2, now time for Theta 1
        # We need to know K1 and K2
        k1[i] = L1 + L2 * cos(rad_Theta2[i]);
        k2[i] = L2 * sin(rad_Theta2[i]);
        rad_Theta1[i] = atan2(y[i], z[i]) - atan2(k2[i], k1[i]);
        Theta1_Deg[i] = degrees(rad_Theta1[i]);

        # Calculate theta3 (angle of 3rd servo)
        Theta3_Deg[i] = 360 - Theta1_Deg[i] - Theta2_Deg[i]


    # test print
    print("VERSION_1 theta1={0}, theta2={1}, theta3={2}".format(Theta1_Deg, Theta2_Deg, Theta3_Deg))

    return Theta1_Deg, Theta2_Deg, Theta3_Deg


# 3d point to angles for spinny arm (not on rail)
# Origin is defined as the first arm joint at the base
# x,y,z input is the desired coordinate of the tip of the pen
def point_to_angles(x, y, z):
    print("point_to_angles({0}, {1}, {2})".format(x, y, z))

    base_angle = atan2(y, x)

    # Radius to arm wrist
    radius = distance(0, 0, x, y) - PEN_R_OFFSET

    # z of arm wrist (wrist is above pen tip)
    z_wrist = z + PEN_Z_OFFSET

    dist_to_origin = distance(0, 0, radius, z_wrist)
    joint_angle1_a = atan2(z_wrist, radius) # angle between horizon and line to wrist

    # L2 is the opposite side for law of cosines.
    joint_angle1_b = law_of_cosines(dist_to_origin, L1, L2)
    joint_angle1 = joint_angle1_a + joint_angle1_b

    # dist_to_origin is the opposite side for law of cosines
    joint_angle2 = law_of_cosines(L1, L2, dist_to_origin)

    print("points_to_angles results: base={0}, joint1={1}, joint2={2}".format(degrees(base_angle), degrees(joint_angle1), degrees(joint_angle2)))

    return degrees(base_angle), degrees(joint_angle1), degrees(joint_angle2)



# 2-d version
def points_to_angles_old2(x, y):
    distance_to_origin = distance(0, 0, x, y)

    # Angle between x-axis and line from origin to (x,y)
    theta1_a = atan2(y, x)

    # L2 is the opposite side for law of cosines.
    theta1_b = law_of_cosines(distance_to_origin, L1, L2)

    theta1 = theta1_a + theta1_b

    # distance_to_origin is the opposite side for law of cosines
    theta2 = law_of_cosines(L1, L2, distance_to_origin)

    # Make L3 form right angle with verticle canvas
    # This makes a pentagon shape, with the 3 arm segments, canvas, and ground as the sides
    # Pentagon angles add up to 540. We know angle between canvas and ground, and canvas and pen are 90 deg
    theta3 = ( 2 * pi ) - theta1 - theta2

    # test print
    # print("points_to_angles results: theta1={0}, theta2={1}, theta3={2}".format(degrees(theta1), degrees(theta2), degrees(theta3)))
    return degrees(theta1), degrees(theta2), degrees(theta3)


def distance(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return sqrt(dy**2 + dx**2)


def law_of_cosines(a, b, c):
    acos_input = (a*a + b*b - c*c) / (2 * a * b)
    if not (-1 < acos_input < 1):
        print "Error: Cannot acos({0})".format(acos_input)
        return 0
    return acos( acos_input )


def mm_to_px(mm):
    return float(mm) * PX_TO_MM_RATIO


def px_to_mm(px):
    return float(px) / PX_TO_MM_RATIO

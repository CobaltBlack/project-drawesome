'''
arm_control.py

This file is for converting the logical drawing instructions (from image processing) into physical units and arm angles.
Then, it sends the physical instructions to motor_control.py to move the actual arm motors.
'''

import time
from math import *
from motor_control import MotorController, MotorCommand, DEFAULT_BASE_ANGLE, DEFAULT_J1_ANGLE, DEFAULT_J2_ANGLE

# Arm segment lengths (units in mm)
L1 = 160.0 # TODO: Update limb lengths
L2 = 160.0
L3 = 50.0
ARM_MAX_LENGTH = L1 + L2
MIN_RADIUS = 180.0  # Closest to the base that the arm can reach

PEN_R_OFFSET = 75.0     # Horizontal offset from wrist of the arm to pen location
PEN_Z_OFFSET = 65.0     # Vertical offset from wrist of arm to tip of pen

GROUND_TO_CANVAS_DISTANCE = 0   # How far above the ground the canvas is
Y_REACH_MAX = 0 # init in calculate_arm_reach()
Y_REACH_MIN = 0 # init in calculate_arm_reach()

GROUND_TO_BASE_HEIGHT = 132.0 # Height from first arm joint to ground

PEN_LIFT_DISTANCE   = 50.0                              # Distance to lift pen off the canvas (mm)
PEN_DOWN_Z          = - GROUND_TO_BASE_HEIGHT      # Pen is on the canvas
PEN_UP_Z            = PEN_DOWN_Z + PEN_LIFT_DISTANCE    # unit in mm

# CANVAS_X_MM = 279.4 # units in mm
# CANVAS_Y_MM = 215.9 # units in mm

CANVAS_X_MM = 160.0 # units in mm
CANVAS_Y_MM = 120.0 # units in mm

#CANVAS_X_PX = 1024
#CANVAS_Y_PX = 786
CANVAS_X_PX = 640
CANVAS_Y_PX = 480

PX_TO_MM_RATIO = CANVAS_Y_PX / CANVAS_Y_MM

CANVAS_TO_POLAR_OFFSET_X = -CANVAS_X_MM / 2
CANVAS_TO_POLAR_OFFSET_Y = CANVAS_Y_MM + MIN_RADIUS # Remember to invert Y; opencv increases Y downwards

ARM_SPEED_MM_PER_S = 0.5
PEN_UP_DOWN_DURATION = 0.1

MM_PER_MOVESLICE = 10

LAW_OF_COSINE_ERROR = -99

class ArmController:

    def __init__(self):
        print "Initializing ArmController..."
        x, y, z = angles_to_points(DEFAULT_BASE_ANGLE, DEFAULT_J1_ANGLE, DEFAULT_J2_ANGLE)
        print 'Initial coordinates:', x, y, z
        self.curr_x = x
        self.curr_y = y
        self.curr_z = z
        self.instructions = []
        self.motor_commands = []

        self.mc = MotorController()


    # Loads instructions and image metadata from image processing
    def load_instructions(self, instructions, img_shape):
        self.instructions = instructions
        self.img_shape = img_shape
        self.img_center_offset_x = (CANVAS_X_PX - img_shape[1]) / 2
        self.img_center_offset_y = (CANVAS_Y_PX - img_shape[0]) / 2

        print ("Loaded {0} drawing instruction(s)".format(len(instructions)))
        print self.img_shape


    # Processes the loaded instructions, then calls starts running the motors on a new thread
    def draw_loaded_instructions(self):
        print 'draw_loaded_instructions'

        # Convert drawing instructions into motor commands
        self.motor_commands = []
        for line in self.instructions:
            print line.to_string()
            self.create_commands_for_line(line)

        # Return to starting position
        self.return_to_initial_position()

        # debug
        #for cmd in self.motor_commands:
        #    print cmd.to_string()

        print 'number of motor commands', len(self.motor_commands)

        # Load commands into MotorController
        # Start draw on seperate thread, so everything else can keep running
        self.mc.run_motor_commands(self.motor_commands)


        # Update status messages etc


    # Parses a line instruction into motor commands
    def create_commands_for_line(self, line):

        # Move to start of line
        x_polar, y_polar = self.canvas_to_polar_coords(line.points[0])
        self.add_motor_commands_in_slices(x_polar, y_polar, PEN_UP_Z, no_slice=True)

        # Move pen down to canvas
        self.pen_down()

         # Move pen to each coordinate of the line (connect-the-dots)
        for point in line.points:
            self.move_to(point)

        self.pen_up()


    # Adds command to move to canvas-coordinate, while keeping same Z
    def move_to(self, coordinate):
        # print "move_to coordinate", coordinate

        x_polar, y_polar = self.canvas_to_polar_coords(coordinate)

        # Skip if already on same pixel
        if x_polar == self.curr_x and y_polar == self.curr_y:
            return

        #print("target", coordinate)
        #print("target polar", x_polar, y_polar)

        # Get angle of final positions of each arm motor
        # angles = points_to_angles([[target_y_mm], [PEN_DOWN_Z]]) # obsolete
        # base_angle, j1_angle, j2_angle = point_to_angles(x_polar, y_polar, self.curr_z)

        # TODO: Slice movement into smaller segments for straight lines
        self.add_motor_commands_in_slices(x_polar, y_polar, self.curr_z)# Adds command to move to canvas-coordinate, while keeping same Z


    def pen_up(self):

        # Skip if pen is already up
        if (self.curr_z == PEN_UP_Z):
            return

        # Get angle of final positions of each arm motor
        # Keep same x and y
        base_angle, joint_angle1, joint_angle2 = point_to_angles(self.curr_x, self.curr_y, PEN_UP_Z)
        self.curr_z = PEN_UP_Z

        # Add to motor command list
        new_command = MotorCommand(base_angle, joint_angle1, joint_angle2, 0, PEN_UP_DOWN_DURATION)
        self.motor_commands.append(new_command)


    def pen_down(self):

        # Skip if pen is already down
        if (self.curr_z == PEN_DOWN_Z):
            return

        # Get angle of final positions of each arm motor
        # Keep same x and y
        base_angle, joint_angle1, joint_angle2 = point_to_angles(self.curr_x, self.curr_y, PEN_DOWN_Z)
        self.curr_z = PEN_DOWN_Z

        # Add to motor command list
        new_command = MotorCommand(base_angle, joint_angle1, joint_angle2, 0, PEN_UP_DOWN_DURATION)
        self.motor_commands.append(new_command)


    # adds motor commands to move to target xyz
    # Updates current xyz
    def add_motor_commands_in_slices(self, target_x, target_y, target_z, no_slice=False):
        # starting coords
        starting_x = self.curr_x
        starting_y = self.curr_y
        starting_z = self.curr_z

        # How far to move in each direction
        dx = target_x - starting_x
        dy = target_y - starting_y
        dz = target_z - starting_z
        move_distance = sqrt(dz**2 + dy**2 + dx**2)

        # Optional no slicing, go straight to target
        if no_slice:

            move_duration = float(move_distance) / ARM_SPEED_MM_PER_S

            base_angle, j1_angle, j2_angle = point_to_angles(target_x, target_y, target_z)
            new_command = MotorCommand(base_angle, j1_angle, j2_angle, 0, move_duration)
            self.motor_commands.append(new_command)

            self.curr_x = target_x
            self.curr_y = target_y
            self.curr_z = target_z
            return

        # Split each movement into equal sized "slices"
        slices = int(round(move_distance / MM_PER_MOVESLICE))
        if slices < 1:
            slices = 1

        dx_per_slice = dx / slices
        dy_per_slice = dy / slices
        dz_per_slice = dz / slices

        for i in range(1, slices + 1):
            next_x = starting_x + (i * dx_per_slice)
            next_y = starting_y + (i * dy_per_slice)
            next_z = starting_z + (i * dz_per_slice)

            base_angle, j1_angle, j2_angle = point_to_angles(next_x, next_y, next_z)
            # TODO: error check to makes

            # TODO: Calculate how fast to move the motors (in seconds)
            move_duration = float(move_distance / slices) / ARM_SPEED_MM_PER_S

            new_command = MotorCommand(base_angle, j1_angle, j2_angle, 0, move_duration)
            self.motor_commands.append(new_command)

        self.curr_x = target_x
        self.curr_y = target_y
        self.curr_z = target_z


    def canvas_to_polar_coords(self, coordinate):

        target_x = coordinate[0]
        target_y = coordinate[1]

        # Convert units to mm
        target_x_mm = px_to_mm(target_x)
        target_y_mm = px_to_mm(target_y)

        # Transform canvas coordinates into polar
        # Also tries to center the image if it doesnt fully fit resolution
        # Invert Y because openCV has y backwards
        polar_x = CANVAS_TO_POLAR_OFFSET_X + (target_x_mm + self.img_center_offset_x)
        polar_y = CANVAS_TO_POLAR_OFFSET_Y - (target_y_mm + self.img_center_offset_y)

        return polar_x, polar_y


    def return_to_initial_position(self):
        new_command = MotorCommand(DEFAULT_BASE_ANGLE, DEFAULT_J1_ANGLE, DEFAULT_J2_ANGLE, 0, PEN_UP_DOWN_DURATION)
        self.motor_commands.append(new_command)


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
        self.mc.drawing_paused = not self.mc.drawing_paused


    def draw_image_abort(self):
        global draw_abort
        self.draw_abort = True
        self.mc.drawing_aborted = True


    def get_drawing_progress(self):
        return self.mc.get_drawing_progress()


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
    #print("point_to_angles({0}, {1}, {2})".format(x, y, z))

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

    #print("points_to_angles results: base={0}, joint1={1}, joint2={2}".format(degrees(base_angle), degrees(joint_angle1), degrees(joint_angle2)))

    return degrees(base_angle), degrees(joint_angle1), degrees(joint_angle2)


def angles_to_points(base, j1, j2):

    # Find radial distance r and z
    j2b = j1 + j2 - 90
    r1 = L1 * cos(radians(j1))
    h1 = L1 * sin(radians(j1))
    r2 = L2 * sin(radians(j2b))
    h2 = L2 * cos(radians(j2b))
    r = r1 + r2 + PEN_R_OFFSET
    z = h1 - h2 - PEN_Z_OFFSET

    # Get x, y based on r and base angle
    x = r * cos(radians(base))
    y = r * sin(radians(base))

    print("angles_to_points({0}, {1}, {2})".format(x, y, z))
    return x, y, z


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


def distance3d(x1, y1, z1, x2, y2, z2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    dz = abs(z2 - z1)
    return sqrt(dz**2 + dy**2 + dx**2)


def law_of_cosines(a, b, c):
    acos_input = (a*a + b*b - c*c) / (2 * a * b)
    if not (-1 < acos_input < 1):
        print "Error: Cannot acos({0})".format(acos_input)
        return LAW_OF_COSINE_ERROR
    return acos( acos_input )


def mm_to_px(mm):
    return float(mm) * PX_TO_MM_RATIO


def px_to_mm(px):
    return float(px) / PX_TO_MM_RATIO

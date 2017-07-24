from math import *

# Arm segment lengths
L1 = 170.0 # units in mm`
L2 = 150.0
L3 = 50.0
ARM_MAX_LENGTH = L1 + L2

GROUND_TO_CANVAS_DISTANCE = 0   # How far above the ground the canvas is
Y_REACH_MAX = 0 # init in calculate_arm_reach()
Y_REACH_MIN = 0 # init in calculate_arm_reach()

BASE_TO_CANVAS_DISTANCE = 100.0 # TBD. Z Distance from arm base to canvas

PEN_LIFT_DISTANCE   = 10.0                              # Distance to lift pen off the canvas (mm)
PEN_DOWN_Z          = -(BASE_TO_CANVAS_DISTANCE - L3)   # z of joint that connects L3
PEN_UP_Z            = PEN_DOWN_Z - PEN_LIFT_DISTANCE    # unit in mm

CANVAS_X_MM = 215.9 # units in mm
CANVAS_Y_MM = 279.4 # units in mm

CANVAS_X_PX = 1080
CANVAS_Y_PX = 1920

PX_TO_MM_RATIO = CANVAS_X_PX / CANVAS_X_MM

ARM_SPEED_MM_PER_S = 10

curr_x = 0
curr_y = 0


class ServoCommand:
    def __init__(self, theta1, theta2, rail_x_mm, pen_select_angle, move_duration):
        self.theta1 = theta1    # Angle of base arm joint in degrees
        self.theta2 = theta2    # Angle of 2nd arm joint in degrees
        self.theta3 = theta3    # Angle of 3rd arm joint in degrees
        self.pen_select_angle = pen_select_angle    # Angle of pen selector servo in degrees
        self.rail_x_mm = rail_x_mm  # x position of rail. Leftmost is 0, rightmost is CANVAS_X_MM
        self.move_duration = move_duration  # Time in seconds to perform the movement


# Main method
def start_drawing(instructions):

    # Initialize robot arm stuffs
    curr_x = 0
    curr_y = 0

    # Calculate reachable y values
    calculate_arm_reach()

    # Process lines in each instruction
    print "arm_control module start..."
    print "Number of instructions received:", len(instructions)
    print "ARM_MAX_LENGTH:", ARM_MAX_LENGTH
    print "PX_TO_MM_RATIO:", PX_TO_MM_RATIO

    for line in instructions:
        draw_line(line)
        pass

    print "arm_control module end!"


def draw_line(line):
    #print 'Drawing line with color:', line.color, '\tStart:', line.points[0], '\tEnd:', line.points[-1]
    # pen-up and select correct color
    pen_up()
    select_pen_color(line.color)

    # move to starting point
    move_to(line.points[0])

    pen_down()

    # Move pen to each coordinate of the line (connect-the-dots)
    for point in line.points:
        move_to(point)

    pen_up()


def move_to(coordinate):
    global curr_x, curr_y

    target_x = coordinate[0]
    target_y = coordinate[1]

    # Skip if already on same pixel
    if target_x == curr_x and target_y == curr_y:
        return

    curr_x = target_x
    curr_y = target_y

    # The arm controls y and z (vertically, and depth of arm)
    # Rail controls x (horizontally)

    # Convert units to mm
    target_x_mm = px_to_mm(target_x)
    target_y_mm = px_to_mm(target_y) + GROUND_TO_CANVAS_DISTANCE

    # Get angle of final positions of each arm motor
    angles = points_to_angles([[target_y_mm], [PEN_DOWN_Z]])

    # Calculate how fast to move the motors (in seconds)
    distance_to_target = distance(curr_x, curr_y, target_x, target_y)
    distance_to_target_mm = px_to_mm(distance_to_target)
    move_duration = distance_to_target_mm / ARM_SPEED_MM_PER_S

    # TODO: Actually move the servos
    # activate_arm_servos(angles, move_duration)
    # activate_rail_servos(target_y_mm, move_duration)


def pen_up():
    # Get angle of final positions of each arm motor
    # Use current y and hardcoded Z value
    curr_y_mm = px_to_mm(curr_y) + GROUND_TO_CANVAS_DISTANCE
    angles = points_to_angles([[curr_y_mm], [PEN_UP_Z]])

    # TODO: Send angles to servo control


def pen_down():
    # Get angle of final positions of each arm motor
    # Use current y and hardcoded Z value
    curr_y_mm = px_to_mm(curr_y) + GROUND_TO_CANVAS_DISTANCE
    angles = points_to_angles([[curr_y_mm], [PEN_DOWN_Z]])

    # TODO: Send angles to servo control


def select_pen_color(color):
    # Find angle of corresponding color based on map
    
    # Send angle to servo control
    pass
    
    
def points_to_angles(points):

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

    for i in range(len(z)):
        # Check point is within arm's reach
        if (distance(0, 0, y[i], z[i]) >= ARM_MAX_LENGTH):
            print "Error: Arm cannot reach y=", y[i], "and z=", z[i]
            continue

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

        # TODO: Calculate theta3 (angle of 3rd servo)


    # test print
    # print "===== Theta1_Deg[], Theta2_Deg[] ====="
    # print Theta1_Deg
    # print Theta2_Deg

    return Theta1_Deg, Theta2_Deg


def calculate_arm_reach():
    global Y_REACH_MAX, Y_REACH_MIN

    # TODO eric: learn how math works
    pass


def distance(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return sqrt(dy**2 + dx**2)


def mm_to_px(mm):
    return float(mm) * PX_TO_MM_RATIO


def px_to_mm(px):
    return float(px) / PX_TO_MM_RATIO

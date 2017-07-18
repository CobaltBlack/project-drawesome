from math import *

# Arm segment lengths
L1 = 13 # units in mm`
L2 = 6
L3 = 5
ARM_MAX_LENGTH = L1 + L2 + L3

PEN_DOWN_Z = -5.0
PEN_UP_Z = -4.0 # units should be in mm

CANVAS_X_MM = 215.9 # units in mm
CANVAS_Y_MM = 279.4 # units in mm

CANVAS_X_PX = 1080
CANVAS_Y_PX = 1920

PX_TO_MM_RATIO = CANVAS_X_PX / CANVAS_X_MM

curr_x = 0
curr_y = 0

#curr_angle

# Main method
def start_drawing(instructions):

    # Initialize robot arm stuffs
    curr_x = 0
    curr_y = 0

    # Process lines in each instruction
    print "Running arm_control module..."
    print "Number of instructions received:", len(instructions)
    for line in instructions:
        draw_line(line)
        pass

    # pen-up when done
    pass


def draw_line(line):
    #print 'Drawing line with color:', line.color, '\tStart:', line.points[0], '\tEnd:', line.points[-1]
    # pen-up and select correct color


    # move to starting point
    move_to(line.points[0])

    # pen-down

    # Move pen to coordinate of the line in sequence
    for point in line.points:
        move_to(point)

    # pen-up

    pass


def move_to(coordinate):
    x = coordinate[0]
    y = coordinate[1]

    # Skip if already on point
    if x == curr_x and y == curr_y:
        return

    # Get angle of final positions of each motor
    points_to_angles([[y], [PEN_DOWN_Z]])

    # Calculate how fast to move the motors

    # Actually move the motors

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
        if (distance(0, 0, y[i], z[i]) > ARM_MAX_LENGTH):
            print "Arm cannot reach y=", y[i], "and z=", z[i]
            continue

        # The length from origin to end effector initializtion
        pos_a[i] = sqrt(1-(((z[i]**2+y[i]**2-L1**2-L2**2)/(2*L2*L1))**2));
        neg_a[i] = -sqrt(1-(((z[i]**2+y[i]**2-L1**2-L2**2)/(2*L2*L1))**2));
        b[i] = ((z[i]**2)+(y[i]**2)-L1**2-L2**2)/(2*L1*L2);

        rad_Theta2[i] = atan2(pos_a[i], b[i]);
        Theta2_Deg[i] = degrees(rad_Theta2[i]);

        # We have calculated Theta2, now time for Theta 1
        # We need to know K1 and K2
        k1[i] = L1 + L2*cos(rad_Theta2[i]);
        k2[i] = L2*sin(rad_Theta2[i]);
        rad_Theta1[i] = atan2(y[i], z[i]) - atan2(k2[i], k1[i]);
        Theta1_Deg[i] = degrees(rad_Theta1[i]);

    # test print
    print "===== Theta1_Deg[], Theta2_Deg[] ====="
    print Theta1_Deg
    print Theta2_Deg

    return Theta1_Deg, Theta2_Deg


def distance(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return sqrt(dy**2 + dx**2)

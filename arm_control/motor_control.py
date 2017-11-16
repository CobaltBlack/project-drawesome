'''
motor_control.py

This file takes the requested angles and positions of the motors and actually coordinate and move them physically.
'''

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

import time
import atexit
import threading

# Since there is no way to check the current angle of the arm,
# we must physically position the arm before starting the program
DEFAULT_BASE_ANGLE = 90
DEFAULT_J1_ANGLE = 90
DEFAULT_J2_ANGLE = 90

GEAR_RATIO = 9.0 / 32.0
ANGLE_PER_STEP = (360.0 / 200.0) * GEAR_RATIO

ST_BASE_DIR_REVERSED = False
ST_J1_DIR_REVERSED = False
ST_J2_DIR_REVERSED = True

STEP_STYLE = Adafruit_MotorHAT.DOUBLE


class MotorCommand:
    def __init__(self, base_angle, j1_angle, j2_angle, pen_grip_angle, move_duration):
        self.base_angle = base_angle
        self.j1_angle = j1_angle
        self.j2_angle = j2_angle

        # self.theta1 = theta1    # Angle of base arm joint in degrees
        # self.theta2 = theta2    # Angle of 2nd arm joint in degrees
        # self.theta3 = theta3    # Angle of 3rd arm joint in degrees
        # self.rail_x_mm = rail_x_mm  # x position of rail. Leftmost is 0, rightmost is CANVAS_X_MM
        self.pen_grip_angle = pen_grip_angle    # Angle of pen selector motor in degrees
        self.move_duration = move_duration  # Time in seconds to perform the movement

    def to_string(self):
        return ("base={0}, j1={1}, j2={2}, pen_gripper={3}mm, duration={4}s".format(
            self.base_angle,
            self.j1_angle,
            self.j2_angle,
            self.pen_grip_angle,
            self.move_duration))


class MotorController():

    def __init__(self):
        # Init both HAT and 3 steppers
        self.bottomhat = Adafruit_MotorHAT(addr=0x60)
        self.tophat = Adafruit_MotorHAT(addr=0x61)

        self.st_base = self.tophat.getStepper(200, 1)   # stepper at base of arm
        self.st_j1 = self.bottomhat.getStepper(200, 1)      # joint1 stepper
        self.st_j2 = self.bottomhat.getStepper(200, 2)      # joint2 stepper
        self.steppers = [self.st_base, self.st_j1, self.st_j2]

        # TODO: Init gripper motor

        self.st_base.setSpeed(60)          # 30 RPM
        self.st_j1.setSpeed(60)          # 30 RPM
        self.st_j2.setSpeed(60)          # 30 RPM

        # Empty threads for running each stepper
        self.st_base_thread = threading.Thread()
        self.st_j1_thread = threading.Thread()
        self.st_j2_thread = threading.Thread()
        # self.st_rail_thread = threading.Thread()

        self.threads = [
            self.st_base_thread,
            self.st_j1_thread,
            self.st_j2_thread
        ]

        # Current angles
        # TODO: Somehow determine starting position
        self.cur_base_angle = DEFAULT_BASE_ANGLE
        self.cur_j1_angle = DEFAULT_J1_ANGLE
        self.cur_j2_angle = DEFAULT_J2_ANGLE
        
        # progress bar
        self.progress_current = 0
        self.progress_total = 0


    def run_motor_commands(self, motor_commands):
        print('Number of motor commands!!:', len(motor_commands))
        self.progress_current = 0
        self.progress_total += len(motor_commands)
        
        for command in motor_commands:
            self.progress_current += 1

            # Calculate angle, and step differences
            # Round to closest integer number of steps
            d_steps_base = int(round((command.base_angle - self.cur_base_angle) / ANGLE_PER_STEP))
            d_steps_j1 = int(round((command.j1_angle - self.cur_j1_angle) / ANGLE_PER_STEP))

            # Geometric/mechanical behaviour of the arm
            target_l2_angle = 180 - command.j1_angle - command.j2_angle
            d_steps_j2 = int(round((target_l2_angle - self.cur_j2_angle) / ANGLE_PER_STEP))

            # Set speed based on calculation with duration??

            # Determine directions to step
            # XOR (^) operator to reverse direction on some motors based on setup
            base_dir = Adafruit_MotorHAT.FORWARD if ((d_steps_base > 0) ^ ST_BASE_DIR_REVERSED) else Adafruit_MotorHAT.BACKWARD
            j1_dir = Adafruit_MotorHAT.FORWARD if ((d_steps_j1 > 0) ^ ST_J1_DIR_REVERSED) else Adafruit_MotorHAT.BACKWARD
            j2_dir = Adafruit_MotorHAT.FORWARD if ((d_steps_j2 > 0) ^ ST_J2_DIR_REVERSED) else Adafruit_MotorHAT.BACKWARD

            # Set up threads for each motor to run simultaneously
            self.st_base_thread = threading.Thread(target=stepper_worker, args=(self.st_base, abs(d_steps_base), base_dir, STEP_STYLE))
            self.st_j1_thread = threading.Thread(target=stepper_worker, args=(self.st_j1, abs(d_steps_j1), j1_dir, STEP_STYLE))
            self.st_j2_thread = threading.Thread(target=stepper_worker, args=(self.st_j2, abs(d_steps_j2), j2_dir, STEP_STYLE))

            self.st_base_thread.start()
            self.st_j1_thread.start()
            self.st_j2_thread.start()

            # Update to new values
            # Calculate current angles based on number of steps moved
            self.cur_base_angle = self.cur_base_angle + (d_steps_base * ANGLE_PER_STEP)
            self.cur_j1_angle = self.cur_j1_angle + (d_steps_j1 * ANGLE_PER_STEP)
            self.cur_j2_angle = self.cur_j2_angle + (d_steps_j2 * ANGLE_PER_STEP)

            # Run commands only if motors are done
            while (self.are_motors_running()):
                time.sleep(0.001)
                pass


        # end for-loop

        self.turnOffMotors()

    # end run_motor_commands()


    # Moves motors to default position
    def move_to_default_position(self):
        pass


    # Returns true if any motor threads are still alive (aka motors are moving)
    def are_motors_running(self):
        for thread in self.threads:
            if thread.isAlive():
                return True
        return False


    # recommended for auto-disabling motors on shutdown!
    def turnOffMotors(self):
        self.bottomhat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.bottomhat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.bottomhat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.bottomhat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
        self.tophat.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        self.tophat.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        self.tophat.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        self.tophat.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


    def get_drawing_progress(self):
        return progress_current/progress_total


# End MotorController


def stepper_worker(stepper, numsteps, direction, style):
    stepper.step(numsteps, direction, style)

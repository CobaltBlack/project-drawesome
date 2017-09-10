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
DEFAULT_PHETA1 = 90
DEFAULT_PHETA2 = 90
DEFAULT_PHETA3 = 90


class MotorCommand:
    def __init__(self, theta1, theta2, theta3, rail_x_mm, pen_select_angle, move_duration):
        self.theta1 = theta1    # Angle of base arm joint in degrees
        self.theta2 = theta2    # Angle of 2nd arm joint in degrees
        self.theta3 = theta3    # Angle of 3rd arm joint in degrees
        self.rail_x_mm = rail_x_mm  # x position of rail. Leftmost is 0, rightmost is CANVAS_X_MM
        self.pen_select_angle = pen_select_angle    # Angle of pen selector motor in degrees
        self.move_duration = move_duration  # Time in seconds to perform the movement

    def to_string(self):
        return ("t1={0}, t2={1}, t3={2}, rail_x={3}mm, duration={4}s".format(self.theta1,
                                                                            self.theta2,
                                                                            self.theta3,
                                                                            self.rail_x_mm,
                                                                            self.move_duration))


class MotorController():

    ANGLE_PER_STEP = 360.0 / 200.0

    def __init__(self):
        # Init HAT and steppers
        self.mh = Adafruit_MotorHAT()

        self.st1 = mh.getStepper(200, 1)      # 200 steps/rev, motor port #1
        self.st2 = mh.getStepper(200, 2)      # 200 steps/rev, motor port #2
        #self.st3 = mh.getStepper(200, 3)      # 200 steps/rev, motor port #3
        #self.st_rail = mh.getStepper(200, 4)      # 200 steps/rev, motor port #4

        self.st1.setSpeed(60)          # 30 RPM
        self.st2.setSpeed(60)          # 30 RPM
        self.st3.setSpeed(60)          # 30 RPM
        self.st_rail.setSpeed(60)          # 30 RPM

        # Empty threads for running each stepper
        self.st1_thread = threading.Thread()
        self.st2_thread = threading.Thread()
        self.st3_thread = threading.Thread()
        self.st_rail_thread = threading.Thread()

        # Current angles
        self.pheta1 = DEFAULT_PHETA1
        self.pheta2 = DEFAULT_PHETA2
        self.pheta3 = DEFAULT_PHETA3

        # Current steps from starting position



    def run_motor_commands(self, motor_commands):
        for command in motor_commands:
            # Run commands only if motors are done
            while (self.are_motors_running()):
                pass

            # Calculate pheta and distance differences
            d_pheta1 = command.pheta1 - self.pheta1
            d_pheta2 = command.pheta2 - self.pheta2
            d_pheta3 = command.pheta3 - self.pheta3

            # Convert differences to number of steps, angle differences to steps
            pending_steps1 = d_pheta1 / ANGLE_PER_STEP
            pending_steps2 = d_pheta2 / ANGLE_PER_STEP
            pending_steps3 = d_pheta3 / ANGLE_PER_STEP
            pending_steps_rail = 0  # TODO calculate rail steps

            # Set speed based on calculation with duration


            # Set up threads for each motor to run simultaneously


            # Update to new values


        # end for-loop

        self.turnOffMotors()

    # end run_motor_commands()


    # Moves motors to default position
    def move_to_default_position(self):
        pass


    # Returns true if any motor threads are still alive (aka motors are moving)
    def are_motors_running(self):
        return (st1_thread.isAlive() or st2_thread.isAlive() or st3_thread.isAlive() or st_rail_thread.isAlive())


    # recommended for auto-disabling motors on shutdown!
    def turnOffMotors(self):
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


# End MotorController


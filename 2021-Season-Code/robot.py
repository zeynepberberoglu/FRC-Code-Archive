import wpilib
import wpilib.drive
import time
import logging
import math
from rev.color import ColorSensorV3

# Using wpilib.TimedRobot class for the main robot program structure
class MyRobot(wpilib.TimedRobot):

    def robotInit(self):
        """
        Initialization phase: Called once when the robot is first powered on.
        All hardware components, sensors, and initial settings are defined here.
        """
        
        # --- Configuration Constants ---
        self.shooter_motor_speed = 0.65
        self.intake_motor_speed = 0.5
        self.chassis_motor_speed = 0.75
        self.belt_motor_speed = 1
        self.hopper_motor_speed = 0.35
        self.stop = 0  # Zero speed constant
        self.mod = 0   # Shooter distance mode selector
        self.timer = wpilib.Timer()

        # --- Pneumatics Solenoid Values ---
        # Note: Assigned solenoid states for clarity
        self.solenoid_forward = wpilib.DoubleSolenoid.Value.kForward
        self.solenoid_reverse = wpilib.DoubleSolenoid.Value.kReverse
        self.solenoid_off = wpilib.DoubleSolenoid.Value.kOff

        # --- Sensors ---
        # Defines the Color Sensor V3 connected to the RoboRIO's Onboard I2C port
        self.colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        # --- Operator Interface (OI) ---
        # Joysticks definition (0 = Xbox controller, 1 = Secondary Joystick)
        self.stick   = wpilib.Joystick(0)  # Drive/Chassis control
        self.stick2 = wpilib.Joystick(1) # Mechanism control

        # --- Compressor (Pneumatics Management) ---
        self.compressor = wpilib.Compressor(10)  # Defines compressor PCM port
        # Enables automatic operation: compressor starts when pressure drops
        self.compressor.setClosedLoopControl(True)

        # --- Solenoids (Pneumatics Actuators) ---
        # Defines DoubleSolenoids for shooter and intake deployment
        self.shooter_solenoid = wpilib.DoubleSolenoid(10, 0, 1) #

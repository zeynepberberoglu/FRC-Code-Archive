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
        self.shooter_solenoid = wpilib.DoubleSolenoid(10, 0, 1) # PCM Channel 0 and 1
        self.intake_solenoid = wpilib.DoubleSolenoid(10, 2, 3) # PCM Channel 2 and 3

        # --- Mechanism Motors (PWMVictorSPX) ---
        # Defines motors for game piece manipulation systems
        self.hopper_motor = wpilib.PWMVictorSPX(5)
        self.shooterRight_motor = wpilib.PWMVictorSPX(6)  
        self.shooterLeft_motor = wpilib.PWMVictorSPX(7)
        self.intake_motor = wpilib.PWMVictorSPX(8)
        self.belt_motor = wpilib.PWMVictorSPX(9)  
        
        # Disabling Safety for mechanisms (Common practice in FRC if handled by code)
        self.hopper_motor.setSafetyEnabled(False)
        self.shooterRight_motor.setSafetyEnabled(False)
        self.shooterLeft_motor.setSafetyEnabled(False)
        self.intake_motor.setSafetyEnabled(False)
        self.belt_motor.setSafetyEnabled(False)
        
        # --- Drive Train Motors ---
        self.right1 = wpilib.PWMVictorSPX(1)                          
        self.right2 = wpilib.PWMVictorSPX(2)
        self.left1 = wpilib.PWMVictorSPX(3)
        self.left2 = wpilib.PWMVictorSPX(4)

        # Disabling Safety for drive motors
        self.right1.setSafetyEnabled(False)
        self.right2.setSafetyEnabled(False)
        self.left1.setSafetyEnabled(False)
        self.left2.setSafetyEnabled(False)

        # --- Motor Grouping ---
        self.right = wpilib.SpeedControllerGroup(self.right1, self.right2) # Group right side motors
        self.left = wpilib.SpeedControllerGroup(self.left1, self.left2)    # Group left side motors
        self.shooters = wpilib.SpeedControllerGroup(self.shooterRight_motor,self.shooterLeft_motor) # Group shooter motors

        # Differential Drive object for standard Arcade control
        self.drive = wpilib.drive.DifferentialDrive(self.left,self.right) 

    # --- Teleoperated Control Functions ---

    def change_speed(self):
        """Allows manual adjustment of chassis drive speed (chassis_motor_speed) via button presses."""
        # Using a lock mechanism (buttons 7 & 8) to enable speed adjustment mode
        while self.stick.getRawButton(7) == True and self.stick.getRawButton(8) == True:
            if self.stick.getRawButtonPressed(3):
                self.chassis_motor_speed += 0.15
                if self.chassis_motor_speed >= 1:
                    self.chassis_motor_speed = 0.95
            elif self.stick.getRawButtonPressed(1):
                self.chassis_motor_speed -= 0.15
                if self.chassis_motor_speed <= 0:
                    self.chassis_motor_speed = 0.05
           
    def shooter_dist(self):
        """
        Allows the operator to select a pre-defined shooter speed (mod) based on target distance.
        This demonstrates distance calibration via software modes.
        """
        while self.stick2.getRawButton(7) == True and self.stick2.getRawButton(8) == True:
            if self.stick2.getRawButtonPressed(4): # Increment mode
                self.mod = self.mod + 1
                if self.mod >= 4:
                    self.mod = 4
            
            elif self.stick2.getRawButtonPressed(3): # Decrement mode
                self.mod = self.mod - 1
                if self.mod <= 0:
                    self.mod = 0
            
            # Map mode number to specific shooter velocity
            if self.mod == 1:
                self.shooter_motor_speed = 0.45 # Green zone
            elif self.mod == 2:
                self.shooter_motor_speed = 0.75 # Yellow zone
            elif self.mod == 3:
                self.shooter_motor_speed = 0.55 # Blue zone
            elif self.mod == 4:
                self.shooter_motor_speed = 0.575 # Pink zone
            
        print("mod",self.mod)

    def shooter_speed(self):
        """Allows fine-tuning of the shooter motor speed parameter."""
        while self.stick2.getRawButton(7) == True and self.stick2.getRawButton(8) == True:
            if self.stick2.getRawButtonPressed(4):
                self.shooter_motor_speed += 0.05
                if self.shooter_motor_speed >= 1:
                    self.shooter_motor_speed = 1
            elif self.stick2.getRawButtonPressed(3):
                self.shooter_motor_speed -= 0.05
                if self.shooter_motor_speed <= 0.5:
                    self.shooter_motor_speed = 0.5
        print(self.shooter_motor_speed)

    def ball_check(self):
        """
        Uses the Color Sensor V3 to detect the presence of a game piece based on
        pre-calibrated RGB color thresholds.
        """
        color = self.colorSensor.getColor() # Read color data from sensor
        
        # Color Thresholding Logic (specific to the game piece's color)
        if 0.35 > color.red > 0.28 and 0.18 > color.blue > 0.07 and 0.6 > color.green > 0.47 :
            print("Ball present")
            return True
        else:
            print("Ball not present")
            return False

    def robot_control(self):
        """Standard Arcade Drive control for the chassis."""
        # Drive: Y-axis (Forward/Backward) * Speed_Scalar, Z-axis (Turning) * Speed_Scalar
        self.drive.arcadeDrive(self.stick.getY()*-self.chassis_motor_speed, self.stick.getZ()*self.chassis_motor_speed)
    
    # --- Solenoid and Basic Motor Controls ---
    # (Functions for individual mechanism control are omitted for brevity, but follow standard pattern)

    def shooter_solenoid_control(self):
        """Controls the shooter angle/deployment using the solenoid."""
        if self.stick2.getRawButton(9):
            self.shooter_solenoid.set(self.solenoid_forward)
        elif self.stick2.getRawButton(10):
            self.shooter_solenoid.set(self.solenoid_reverse)
        else:
            self.shooter_solenoid.set( self.solenoid_off)
    
    def intake_solenoid_control(self):
        """Controls the intake deployment/retraction."""
        if self.stick2.getRawButton(7):
            self.intake_solenoid.set(self.solenoid_forward)
        elif self.stick2.getRawButton(8):
            self.intake_solenoid.set(self.solenoid_reverse)
        else:
            self.intake_solenoid.set(self.solenoid_off)

    # --- Automated Sequential Routines ---

    def ball_take(self):
        """
        Automated sequence for acquiring the game piece.
        Uses nested while loops to enforce multi-step logic (search -> capture -> stage).
        """
        while self.stick2.getRawButton(1):
            self.robot_control() # Allow drive control during sequence

            # State 1: Search and Acquire (Ball not present)
            while self.ball_check() == False and self.stick2.getRawButton(1) == True:
                self.robot_control()
                self.intake_solenoid.set(self.solenoid_forward) # Deploy intake
                self.shooter_solenoid.set(self.solenoid_reverse) # Set shooter angle
                self.shooters.set(self.shooter_motor_speed) # Run shooter pre-emptively
                self.hopper_motor.set(-self.hopper_motor_speed) # Run hopper/storage
                self.intake_motor.set(self.intake_motor_speed) # Run intake motor
                self.belt_motor.set(self.stop) # Belt is OFF during intake
                self.ball_check()
                
            # State 2: Staging (Ball is present)
            while self.ball_check() == True and self.stick2.getRawButton(1) == True:
                self.robot_control()
                self.timer.reset()
                self.timer.start()

                # Run belt for a fixed duration (3.5s) to stage the ball in the shooter
                while self.timer.get() <= 3.5:
                    self.robot_control()
                    self.belt_motor.set(self.belt_motor_speed) # Run belt
                    self.shooters.set(self.stop) # Stop shooter motors (staging)
                    self.hopper_motor.set(-self.hopper_motor_speed)
                    self.intake_motor.set(self.stop)
                    self.timer.get()
                
                self.ball_check() # Re-check status

        # Final Cleanup: Stop all mechanism motors
        self.shooters.set(self.stop)
        self.hopper_motor.set(self.stop)
        self.belt_motor.set(self.stop)
        self.intake_motor.set(self.stop)

    def ball_shoot(self):
        """
        Automated sequence for firing the game piece.
        """
        self.robot_control()
        
        while self.stick2.getRawButton(1) == True:
            # State 1: Spin-up (Ball not present but preparing to shoot)
            while self.ball_check() == False and self.stick2.getRawButton(1) == True:
                self.robot_control()
                self.shooter_solenoid.set(self.solenoid_forward) # Set firing angle
                self.belt_motor.set(-self.belt_motor_speed) # Run belt backwards? (Possible cleanup)
                self.shooters.set(-self.shooter_motor_speed/2) # Pre-spin shooter motors
                self.hopper_motor.set(self.stop) 
                self.intake_motor.set(self.stop)
                self.ball_check()

            # State 2: Firing (Ball is present, full power to shooter)
            while self.ball_check() == True and self.stick2.getRawButton(1) == True:
                self.robot_control()

                self.shooter_solenoid.set(self.solenoid_forward) # Set firing angle
                self.belt_motor.set(-self.belt_motor_speed)
                self.shooters.set(-self.shooter_motor_speed) # Full speed fire
                self.hopper_motor.set(self.hopper_motor_speed) # Feed ball
                self.intake_motor.set(self.stop)
                self.ball_check()

        # Final Cleanup: Stop all mechanism motors and solenoids
        self.shooter_solenoid.set(self.solenoid_off)
        self.belt_motor.set(self.stop)
        self.shooters.set(self.stop)
        self.hopper_motor.set(self.stop)
        self.intake_motor.set(self.stop)

    # --- Periodic Loop ---
    def teleopPeriodic(self):
        """
        Periodic loop: Called approximately every 20ms during the teleoperated period.
        This is the main loop where control functions are called.
        """
        self.robot_control() # Chassis drive is always active
        self.ball_check()    # Sensor data is always active
        
        # Example of active/disabled mechanism control routines:
        # self.ball_take()
        self.ball_shoot() # Currently active sequence
        # self.ball_place()
        
        # Other simple controls:
        self.change_speed()  # Dynamic chassis speed control
        self.shooter_dist()  # Dynamic shooter distance mode selector
        # print("chassis motor",self.chassis_motor_speed)
        # print("shooter motor" , self.shooter_motor_speed)

        
if __name__ == "__main__":
    # Standard WPILib launch command
    wpilib.run(MyRobot)

import wpilib
import wpilib.drive
import time
import logging
import math
from rev.color import ColorSensorV3

class MyRobot(wpilib.TimedRobot):

    def robotInit(self):

        self.shooter_motor_speed = 0.65
        self.intake_motor_speed = 0.5
        self.chassis_motor_speed = 0.75
        self.belt_motor_speed = 1
        self.hopper_motor_speed = 0.35
        self.stop = 0
        self.mod = 0
        self.timer = wpilib.Timer()


        #solenoid atamalarından emin değilim
        self.solenoid_forward = wpilib.DoubleSolenoid.Value.kForward
        self.solenoid_reverse = wpilib.DoubleSolenoid.Value.kReverse
        self.solenoid_off = wpilib.DoubleSolenoid.Value.kOff


        self.colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)    #renk sensörünün bağlı olduğu I2C portunu tanımlıyor


        #joystickler tanımlandı(0=xbox, 1=joystick)
        self.stick   = wpilib.Joystick(0) 
        self.stick2 = wpilib.Joystick(1)


        self.compressor = wpilib.Compressor(10)  #kompresör portu belirtildi
        self.compressor.setClosedLoopControl(True) #Basınç düştüğünde kompresör otomatik olarak açılacaksa True döndürür.


        #solenoidler tanımlanıyor
        self.shooter_solenoid = wpilib.DoubleSolenoid(10,0, 1) #(bağlandığı modül(sabit),PCM e bağladığımız pin,PCM e bağladığımız pin)
        self.intake_solenoid = wpilib.DoubleSolenoid(10, 2, 3)


        #motorlar tanımlanıyor, güvenlikleri kapatılıyor
        self.hopper_motor =  wpilib.PWMVictorSPX(5)
        self.shooterRight_motor = wpilib.PWMVictorSPX(6)  
        self.shooterLeft_motor = wpilib.PWMVictorSPX(7)
        self.intake_motor = wpilib.PWMVictorSPX(8)
        self.belt_motor = wpilib.PWMVictorSPX(9)  
        
        self.hopper_motor.setSafetyEnabled(False)
        self.shooterRight_motor.setSafetyEnabled(False)
        self.shooterLeft_motor.setSafetyEnabled(False)
        self.intake_motor.setSafetyEnabled(False)
        self.belt_motor.setSafetyEnabled(False)
        

        #TEKERLER tanımlanıyor, güvenlikleri kapatılıyor
        self.right1 = wpilib.PWMVictorSPX(1)                          
        self.right2 = wpilib.PWMVictorSPX(2)
        self.left1 = wpilib.PWMVictorSPX(3)
        self.left2 = wpilib.PWMVictorSPX(4)

        self.right1.setSafetyEnabled(False)
        self.right2.setSafetyEnabled(False)
        self.left1.setSafetyEnabled(False)
        self.left2.setSafetyEnabled(False)

        self.right = wpilib.SpeedControllerGroup(self.right1, self.right2) #sağ tekerler gruplandırıldı
        self.left = wpilib.SpeedControllerGroup(self.left1, self.left2) #sol tekerler gruplandırıldı
        self.shooters = wpilib.SpeedControllerGroup(self.shooterRight_motor,self.shooterLeft_motor)

        self.drive = wpilib.drive.DifferentialDrive(self.left,self.right) #arcade driveda kullanmak için surus nesnesi olusturuldu ve şase motorları tanımlandı

    def change_speed(self):
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
        
        while self.stick2.getRawButton(7) == True and self.stick2.getRawButton(8) == True:
            if self.stick2.getRawButtonPressed(4):
                self.mod = self.mod + 1
                if self.mod >= 4:
                    self.mod = 4
            
            elif self.stick2.getRawButtonPressed(3):
                self.mod = self.mod - 1
                if self.mod <= 0:
                    self.mod = 0
            #mod 0 - bölge 3
            if self.mod == 1:
                self.shooter_motor_speed = 0.45 #yeşil bölge
            elif self.mod == 2:
                self.shooter_motor_speed = 0.75 #sarı bölge
            elif self.mod == 3:
                self.shooter_motor_speed = 0.55 #mavi bölge
            elif self.mod == 4:
                self.shooter_motor_speed = 0.575 #pembe bölge
            

        
        

        print("mod",self.mod)

    def shooter_speed(self):
        while self.stick2.getRawButton(7) == True and self.stick2.getRawButton(8) == True:
            if self.stick2.getRawButtonPressed(4):
                self.shooter_motor_speed += 0.05
                if self.shooter_motor_speed >= 1:
                    self.shooter_motor_speed = 1
            elif self.stick2.getRawButtonPressed(3):
                self.shooter_motor_speed -= 0.05
                if self.shooter_motor_speed <= 0.5:
                    self.shooter_motor_speed = 0.5
            #print("Şase motor",self.chassis_motor_speed)
        print(self.shooter_motor_speed)

    def ball_check(self):
        color = self.colorSensor.getColor() #sensörden renk alıyor
        
        if 0.35 > color.red > 0.28 and  0.18 >color.blue > 0.07 and 0.6 > color.green > 0.47 :#topun rengi
            print("top var")
            return True
        else:
            print("top yok")
            return False

    def robot_control(self):
        self.drive.arcadeDrive(self.stick.getY()*-self.chassis_motor_speed,self.stick.getZ()*self.chassis_motor_speed) #(ileri-geri,sağ-sol)
    
    def shooter_control(self):
            if self.stick2.getRawButton(4):
                self.shooterRight_motor.set(self.shooter_motor_speed)
                self.shooterLeft_motor.set(-self.shooter_motor_speed)
            elif self.stick2.getRawButton(3):
                self.shooterRight_motor.set(-self.shooter_motor_speed)
                self.shooterLeft_motor.set(self.shooter_motor_speed)
            elif self.stick2.getRawButton(4) == False and self.stick2.getRawButton(3) == False:
                self.shooterRight_motor.set(self.stop)
                self.shooterLeft_motor.set(self.stop)

    def intake_control(self):
        if self.stick2.getRawButton(11):
            self.intake_motor.set(self.intake_motor_speed)
        elif self.stick2.getRawButton(12):
            self.intake_motor.set(-self.intake_motor_speed)
        elif self.stick2.getRawButton(11) == False and self.stick2.getRawButton(12) == False:
            self.intake_motor.set(self.stop)
    
    def hopper_control(self):  
        if self.stick2.getRawButton(5):
            self.hopper_motor.set(-self.hopper_motor_speed)
            self.belt_motor.set(self.belt_motor_speed)
        elif self.stick2.getRawButton(6):
            self.hopper_motor.set(self.hopper_motor_speed)
            self.belt_motor.set(-self.belt_motor_speed)
        elif self.stick2.getRawButton(5) == False and self.stick2.getRawButton(6) == False:
            self.hopper_motor.set(self.stop)
            self.belt_motor.set(self.stop)

    def shooter_solenoid_control(self):
        if self.stick2.getRawButton(9):
            self.shooter_solenoid.set(self.solenoid_forward)
        elif self.stick2.getRawButton(10):
            self.shooter_solenoid.set(self.solenoid_reverse)
        elif self.stick2.getRawButton(9) == False and self.stick2.getRawButton(10) == False:
            self.shooter_solenoid.set( self.solenoid_off)
    
    def intake_solenoid_control(self):
        if self.stick2.getRawButton(7):
            self.intake_solenoid.set(self.solenoid_forward)
        elif self.stick2.getRawButton(8):
            self.intake_solenoid.set(self.solenoid_reverse)
        elif self.stick2.getRawButton(7) == False and self.stick2.getRawButton(8) == False:
            self.intake_solenoid.set(self.solenoid_off)

    def ball_take(self):

        while self.stick2.getRawButton(1):
            self.robot_control()

            while self.ball_check() == False and self.stick2.getRawButton(1) == True:
                self.robot_control()
                self.intake_solenoid.set(self.solenoid_forward)

                self.shooter_solenoid.set(self.solenoid_reverse)
                self.shooters.set(self.shooter_motor_speed)
                self.hopper_motor.set(-self.hopper_motor_speed)
                self.intake_motor.set(self.intake_motor_speed)
                self.belt_motor.set(self.stop)
                self.ball_check()
                self.stick2.getRawButton(1)

            while self.ball_check() == True and self.stick2.getRawButton(1) == True:

                self.robot_control()
                self.timer.reset()
                self.timer.start()

                while self.timer.get() <= 3.5:
                    self.robot_control()
                    self.belt_motor.set(self.belt_motor_speed)
                    self.shooters.set(self.stop)
                    self.hopper_motor.set(-self.hopper_motor_speed)
                    self.intake_motor.set(self.stop)
                    self.timer.get()

                self.stick2.getRawButton(1)
                self.ball_check()
                    
        self.shooters.set(self.stop)
        self.hopper_motor.set(self.stop)
        self.belt_motor.set(self.stop)
        self.intake_motor.set(self.stop)
        self.stick2.getRawButton(1)

    def ball_shoot(self):
        
        self.robot_control()
        
        while self.stick2.getRawButton(1) == True:
            
            while self.ball_check() == False and self.stick2.getRawButton(1) == True:
                self.robot_control()

                self.shooter_solenoid.set(self.solenoid_forward)
                self.belt_motor.set(-self.belt_motor_speed)
                self.shooters.set(-self.shooter_motor_speed/2)
                self.hopper_motor.set(self.stop)
                self.intake_motor.set(self.stop)
                self.ball_check()
                self.stick2.getRawButton(2)

            while self.ball_check() == True and self.stick2.getRawButton(1) == True:
                self.robot_control()

                self.shooter_solenoid.set(self.solenoid_forward)
                self.belt_motor.set(-self.belt_motor_speed)
                self.shooters.set(-self.shooter_motor_speed)
                self.hopper_motor.set(self.hopper_motor_speed)
                self.intake_motor.set(self.stop)
                self.ball_check()
                self.stick2.getRawButton(2)

        self.shooter_solenoid.set(self.solenoid_off)
        self.belt_motor.set(self.stop)
        self.shooters.set(self.stop)
        self.hopper_motor.set(self.stop)
        self.intake_motor.set(self.stop)

    def ball_place(self):
        self.robot_control()
        
        while self.stick2.getRawButton(3):

            while self.ball_check() == False and self.stick2.getRawButton(3):
                self.robot_control()

                self.shooter_solenoid.set(self.solenoid_reverse)
                self.belt_motor.set(-self.belt_motor_speed)
                self.shooters.set(-self.shooter_motor_speed/4)
                self.hopper_motor.set(self.stop)
                self.intake_motor.set(self.stop)
                self.ball_check()
                self.stick2.getRawButton(3)

            while self.ball_check() == True and self.stick2.getRawButton(3):
                self.robot_control()

                self.shooter_solenoid.set(self.solenoid_reverse)
                self.belt_motor.set(-self.belt_motor_speed)
                self.shooters.set(-self.shooter_motor_speed/4)
                self.hopper_motor.set(self.hopper_motor_speed)
                self.intake_motor.set(self.stop)
                self.ball_check()
                self.stick2.getRawButton(3)

        self.intake_solenoid.set(self.solenoid_forward)
        self.shooter_solenoid.set(self.solenoid_off)
        self.belt_motor.set(self.stop)
        self.shooters.set(self.stop)
        self.hopper_motor.set(self.stop)
        self.intake_motor.set(self.stop)


    def teleopPeriodic(self):

        self.robot_control()
        self.ball_check()
        #self.ball_take()
        self.ball_shoot()
        #self.ball_place()
        #self.intake_solenoid_control()
        #self.shooter_solenoid_control()
        #self.intake_control()
        #self.hopper_control() 
        #self.shooter_control()
        self.change_speed()
        self.shooter_dist()
        #print("Şase motor",self.chassis_motor_speed)
        #print("shooter motor" , self.shooter_motor_speed)

        
if __name__ == "__main__":
    wpilib.run(MyRobot)

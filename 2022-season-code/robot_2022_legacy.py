import wpilib
from wpilib.drive import MecanumDrive
import commands2
import rev
import wpimath
import photonvision
from photonvision import PhotonUtils
from wpimath.controller import PIDController
import math
import ctre
import wpilib.drive
class MyRobot(wpilib.TimedRobot):
    # Portlar tanımlandı (Portları örnek yazdım,değişmeli)
    CAMERA_HEIGHT_METRES = 1
    TARGET_HEIGHT_METRES = 1
    solOnMotorPort = 0
    solArkaMotorPort = 2
    sagOnMotorPort = 1
    sagArkaMotorPort = 3
    cimAciMotorId = 7
    joystickPort = 0
    joystick2port = 1
    pushButtonPort1 = 5
    pushButtonPort2 = 4
    shooteronhiz = 1
    shooterarkahiz = 1
    CAMERA_HEIGHT_METRES = 0.76
    TARGET_HEIGHT_METRES = 1.76
    CAMERA_PITCH_RADIANS = 0.25
    GOAL_RANGE_METERS = 2.3
    shooterVal = 1
    servoCommand = 1
    servoDef = 0.4 # yukari
    servoTop = 0.8 
    servoBall = 0.9
    servoTape = 0.4
    allience = 0 #kırmızı ittifak için 0, mavi ittifak için 2
    def robotInit(self):
        self.cam = photonvision.PhotonCamera("camera1")
        LINEAR_P = 0.2
        LINEAR_D = 0


        ANGULAR_P = 0.02
        ANGULAR_D = 0

        self.turnController = PIDController(ANGULAR_P, 0.01, ANGULAR_D)
        self.forwardController = PIDController(LINEAR_P, 0.1, LINEAR_D)
        self.top = 0
    
        self.timer = wpilib.Timer()
        
        # #Joystick tanımlandı
        self.stick = wpilib.Joystick(self.joystickPort)
        self.stick2 = wpilib.Joystick(self.joystick2port)
        
        #Encoderlar
        self.cimAciEncoder = wpilib.Encoder(2, 3, reverseDirection=False, encodingType=wpilib.Encoder.EncodingType.k4X)
        self.cimAciEncoder.setDistancePerPulse(1 / 20)
        self.saseSagArkaEncoder = wpilib.Encoder(1, 0, reverseDirection=True, encodingType=wpilib.Encoder.EncodingType.k4X)
        self.saseSagArkaEncoder.setDistancePerPulse(1 / 2048)
        # #Motorlar tanımlandı
        self.solOnMotor = wpilib.PWMVictorSPX(self.solOnMotorPort)
        self.solArkaMotor = wpilib.PWMVictorSPX(self.solArkaMotorPort)
        self.sagOnMotor = wpilib.PWMVictorSPX(self.sagOnMotorPort)
        self.sagArkaMotor = wpilib.PWMVictorSPX(self.sagArkaMotorPort)
        
        #Servo
        self.servoMotor = wpilib.Servo(9)
        #Shooterlar
        self.onShooter1 = ctre.VictorSPX(10)
        self.onShooter2 = ctre.VictorSPX(8)
        self.arkaShooter = ctre.VictorSPX(9)
        self.cimAciMotor = ctre.VictorSPX(5)
        self.cimIpMotor = ctre.VictorSPX(4)
        self.alt_belt1 = ctre.VictorSPX(7)
        self.ust_belt1 = ctre.VictorSPX(6)
        #Pushbutton atamasi
        self.pushbuton1 = wpilib.DigitalInput(self.pushButtonPort1)
        self.pushbuton2 = wpilib.DigitalInput(self.pushButtonPort2)
        # #Motor Hız Tanımlamaları
        self.sagArkaMotor.set(0.1)
        self.sagOnMotor.set(0.1)
        self.solArkaMotor.set(0.1)
        self.solOnMotor.set(0.1)

        self.solArkaMotor.setInverted(1)
        self.sagArkaMotor.setInverted(1)
        
        self.onShooter2.setInverted(1)

        self.onShooter1.configVoltageCompSaturation(12)      
        self.onShooter1.enableVoltageCompensation(1)

        self.onShooter2.configVoltageCompSaturation(12)      
        self.onShooter2.enableVoltageCompensation(1)
        
        # self.onShooter2.follow(masterToFollow=self.onShooter1, followerType=ctre.FollowerType.PercentOutput)

        #wpilib kütüphanesi kullanılarak motorlar gruplanıyor
        self.drive = MecanumDrive(
            self.solOnMotor,
            self.sagOnMotor,
            self.solArkaMotor,
            self.sagArkaMotor,
        )


        self.drive.setExpiration(0.1)
        self.drive.setSafetyEnabled(0)

    def autoAimTape(self):
        print("a")
        self.servoMotor.set(self.servoTape) #kamera servosunu ayarlar
        if self.cam.getLatestResult().hasTargets() >= 1: #reflektif algılıyor mu
            print("as")
            self.range = PhotonUtils.calculateDistanceToTarget(0.92, 2.63, 0.51, self.getPitchCVT_Radians())
            print("range",self.range)
            self.rotationSpeed = -(self.turnController.calculate(self.cam.getLatestResult().getBestTarget().getYaw(), 0))
            self.forwardSpeed = -self.forwardController.calculate(self.range, self.GOAL_RANGE_METERS)

            self.turnController.setTolerance(0.1)
            self.forwardController.setTolerance(0.1)
            print("rotationspeed", self.rotationSpeed)
            print("forwardspeed", self.forwardSpeed)
            if self.turnController.atSetpoint() and self.forwardController.atSetpoint():
                self.top = self.top_atma()
            
            else:
                self.drive.driveCartesian(
                        self.stick.getX(), self.forwardSpeed, self.rotationSpeed, 0
                )
            #return self.top
            
        else:
            print("cikti yok")
            self.rotationSpeed = 0
            self.forwardSpeed = 0

            self.drive.driveCartesian(
                self.stick.getX(), -self.stick.getY(), 0, 0
            )

    def autoAimBall(self):
        print("a")
        self.servoMotor.set(self.servoBall)

        if self.cam.getLatestResult().hasTargets() >= 1: 
            print("as")
            # range = PhotonUtils.calculateDistanceToTarget(0.76, 1.76, 0.25, self.getPitchCVT_Radians())
            # print(range)
            self.rotationSpeed = -(self.turnController.calculate(self.cam.getLatestResult().getBestTarget().getYaw(), 0))
            print(self.rotationSpeed)
            rangeToBall = PhotonUtils.calculateDistanceToTarget(0.92, 0.13, -1.37, self.getPitchCVT_Radians())
            self.forwardSpeed = -self.forwardController.calculate(rangeToBall, -0.3)
            self.turnController.setTolerance(0.1)
            if self.turnController.atSetpoint():
                print("aadf")
                self.timer.start()
                self.timer.reset()
                while self.timer.get() < 1.5:
                    # self.rotationSpeed = -(self.turnController.calculate(self.cam.getLatestResult().getBestTarget().getYaw(), 0))
                    self.drive.driveCartesian(
                        self.stick.getX(), 0.3, 0, 0
                    )
                    self.alt_belt1.set(ctre.ControlMode.PercentOutput, -1)
                self.timer.stop()
                self.saseSagArkaEncoder.reset()
                self.top = self.top_alma()
            else:
                self.drive.driveCartesian(
                        self.stick.getX(), 0, self.rotationSpeed, 0
                )
            return self.top
        else:
            print("cikti yok")
            self.rotationSpeed = 0
            self.forwardSpeed = 0


            # self.drive.driveCartesian(
            #     self.stick.getX(), self.forwardSpeed * 2, self.rotationSpeed * 0.1, 0
        #     )
            self.drive.driveCartesian(
                self.stick.getX(), -self.stick.getY(), 0.2, 0
            )


    def autoAimTapeAutonomous(self):
        print("a")
        self.servoMotor.set(self.servoTape)
        self.cam.setPipelineIndex(1)
        if self.cam.getLatestResult().hasTargets() >= 1: 
            print("as")
            self.range = PhotonUtils.calculateDistanceToTarget(0.92, 0.13, 0.61, self.getPitchCVT_Radians())

            self.rotationSpeed = -(self.turnController.calculate(self.cam.getLatestResult().getBestTarget().getYaw(), 0))
            self.forwardSpeed = -self.forwardController.calculate(range, self.GOAL_RANGE_METERS)

            self.turnController.setTolerance(0.1)
            self.forwardController.setTolerance(0.1)

            if self.turnController.atSetpoint() and self.forwardController.atSetpoint():
                self.top = self.top_atma()
            else:
                self.drive.driveCartesian(
                        self.stick.getX(), self.forwardSpeed, self.rotationSpeed, 0
                )
            # return self.top
        else:
            print("cikti yok")
            self.rotationSpeed = 0
            self.forwardSpeed = 0

            self.drive.driveCartesian(
                self.stick.getX(), -self.stick.getY(), 0.2, 0
            )

    def autoAimBallAutonomous(self):
        print("a")
        self.servoMotor.set(self.servoBall)
        self.cam.setPipelineIndex(self.allience)
        
        if self.cam.getLatestResult().hasTargets() >= 1: 
            print("as")
            # range = PhotonUtils.calculateDistanceToTarget(0.76, 1.76, 0.25, self.getPitchCVT_Radians())
            # print(range)
            self.rotationSpeed = -(self.turnController.calculate(self.cam.getLatestResult().getBestTarget().getYaw(), 0))
            print(self.rotationSpeed)
            rangeToBall = PhotonUtils.calculateDistanceToTarget(0.92, 0.13, -1.37, self.getPitchCVT_Radians())
            self.forwardSpeed = -self.forwardController.calculate(rangeToBall, -0.3)
            self.turnController.setTolerance(0.1)
            if self.turnController.atSetpoint():
                print("aadf")
                self.timer.start()
                self.timer.reset()
                while self.timer.get() < 1:
                    self.rotationSpeed = -(self.turnController.calculate(self.cam.getLatestResult().getBestTarget().getYaw(), 0))
                    self.drive.driveCartesian(
                        self.stick.getX(), 0.3, self.rotationSpeed, 0
                    )
                    self.alt_belt1.set(ctre.ControlMode.PercentOutput, -1)
                self.timer.stop()
                self.saseSagArkaEncoder.reset()
                self.top = self.top_alma()
            else:
                self.drive.driveCartesian(
                        self.stick.getX(), 0, self.rotationSpeed, 0
                )
        else:
            print("cikti yok")
            self.rotationSpeed = 0
            self.forwardSpeed = 0

            # self.drive.driveCartesian(
            #     self.stick.getX(), self.forwardSpeed * 2, self.rotationSpeed * 0.1, 0
            #     )
            self.drive.driveCartesian(
                self.stick.getX(), -self.stick.getY(), 0.2, 0
            )


    def getPitchCVT_Radians(self):
        return (self.cam.getLatestResult().getBestTarget().getPitch() * math.pi / 180)

    # def cizgi_renk(self):
    #     colorVal = self.colorSensor.getColor()
    #     if 0.45 > colorVal.red > 0.26 and  0.25 > colorVal.blue > 0.15 and 0.45 > colorVal.green > 0.35:
    #         return True
    def rangeToTapeFunc(self):
        if self.cam.getLatestResult().hasTargets() >= 1: 
            self.rangeToTape = PhotonUtils.calculateDistanceToTarget(0.92, 0.13, 0.61, self.getPitchCVT_Radians())
            print(self.rangeToTape)


    def atis1_2(self):
        self.onShooter1.set(ctre.ControlMode.PercentOutput,self.shooteronhiz)
        self.onShooter2.set(ctre.ControlMode.PercentOutput,self.shooteronhiz)
        self.arkaShooter.set(ctre.ControlMode.PercentOutput,-self.shooterarkahiz)

    def atis1_2stop(self):
        self.onShooter1.set(ctre.ControlMode.PercentOutput,0)
        self.onShooter2.set(ctre.ControlMode.PercentOutput,0)
        self.arkaShooter.set(ctre.ControlMode.PercentOutput,0)
        
    #     # self.atisMotor3.set(0)    

    def top_alma(self): 
        if self.top == 0: #Top Yoksa
            while self.pushbuton2.get() == 0 and self.stick2.getRawButtonPressed(8) == False: #Top içeri girene kadar en alttaki 2 belti çalıştır
                print("sus")
                self.alt_belt1.set(ctre.ControlMode.PercentOutput,-1)
                self.teleopdriveMecanum()
                print(self.pushbuton2.get())
            self.top += 1 
            self.timer.start()
            self.timer.reset()
            while self.timer.get() <= 3:
                print("amogus)")
                self.teleopdriveMecanum()
                self.ust_belt1.set(ctre.ControlMode.PercentOutput,-1)
        
            self.alt_belt1.set(ctre.ControlMode.PercentOutput,0)
            while self.pushbuton1.get() == 0:
                print("gus")
                self.teleopdriveMecanum() 
                #Top üstteki belte gelene kadar üst belti çalıştır
                self.ust_belt1.set(ctre.ControlMode.PercentOutput,-1)
            self.ust_belt1.set(ctre.ControlMode.PercentOutput,0) 
        elif self.top == 1: #Top varsa
            while self.pushbuton2.get() == 0: #Top içeri girene kadar en alttaki 2 belti çalıştır
                print("amog")
                self.teleopdriveMecanum()
                self.alt_belt1.set(ctre.ControlMode.PercentOutput,-1)
            self.alt_belt1.set(ctre.ControlMode.PercentOutput,0)  #Top içeri girince motorları durdur
            self.top += 1
        return self.top #Top sayısını fonksiyonun dışına aktar 
    
    def top_atma(self): 
        while self.pushbuton1.get() == True: #Top atış tekerlerine gelene kadar üst belti çalıştır
            print("asd")
            self.ust_belt1.set(ctre.ControlMode.PercentOutput,-1)
            self.onShooter1.set(ctre.ControlMode.PercentOutput,0.75)
            self.onShooter2.set(ctre.ControlMode.PercentOutput,0.75)
            self.arkaShooter.set(ctre.ControlMode.PercentOutput,-0.9)       
            print(self.pushbuton1.get())
            self.teleopdriveMecanum()
        self.ust_belt1.set(ctre.ControlMode.PercentOutput,0) #top atış tekerlerine gelince atış tekerlerini çalıştır
        print("a")
        self.timer.start()
        #3 saniye bekle
        self.timer.reset()
        while self.timer.get() <= 1:
            pass
        self.timer.reset()
        self.atis1_2stop() #atış bittikten sonra atış tekerlerini durdur
        self.top += -1 #top sayısını 1 azalt
        if self.top == 1: #içerde 1 top daha varsa
            while self.pushbuton2.get() == False: #Top üstteki belte gelene kadar alttaki motorları çalıştır
                self.alt_belt1.set(ctre.ControlMode.PercentOutput,-1)
                self.ust_belt1.set(ctre.ControlMode.PercentOutput,-1)
                self.teleopdriveMecanum()
            self.alt_belt1.set(ctre.ControlMode.PercentOutput,0) #Top üstdaki belte gelince alttaki motorları durdur
            while self.pushbuton1.get() == False: #Top atış tekerlerine gelene kadar üst belti çalıştır
                self.teleopdriveMecanum()
            self.atis1_2()   #Top atış tekerlerine gelince atış tekerlerini çalıştır 
            #3 saniye bekle
            self.timer.reset()
            while self.timer.get() <= 1:
                pass
            self.timer.reset()
            self.atis1_2stop() #atış bittikten sonra atış tekerlerini durdur
        self.ust_belt1.set(ctre.ControlMode.PercentOutput,0) #üst belti durdur
        return self.top
    

    def teleopdriveMecanum(self):

        self.rotate = 0
        if abs(self.stick2.getZ()) > abs(self.stick.getZ()):
            self.rotate = self.stick2.getZ() * 0.3
        
        else:
            self.rotate = self.stick.getZ()


        self.drive.driveCartesian(
            self.stick.getX(), -self.stick.getY(), self.rotate, 0
        )
    def servoButon(self):
        if self.stick.getRawButtonPressed(11):
            self.servoCurrent += 0.1
        elif self.stick.getRawButtonPressed(12):
            self.servoCurrent -= 0.1
        
    def frontShooterSpeedConfig(self):
        return ((self.shooterVal * 0,8)  * 0,9)
    def rearShooterSpeedConfig(self):
        return (-(self.shooterVal * 0,8) * 1,2)
        
    def cimAciManuel(self):
        if self.stick.getRawButton(7) == True:
            self.cimAciMotor.set(ctre.ControlMode.PercentOutput,1)
        elif self.stick.getRawButton(8) == True:
            self.cimAciMotor.set(ctre.ControlMode.PercentOutput,-1)
        elif self.stick.getRawButton(7) == False and self.stick.getRawButton(8) == False:
            self.cimAciMotor.set(ctre.ControlMode.PercentOutput,0)
        elif self.stick.getRawButton(3) == True:
            self.cimAciMotor.set(ctre.ControlMode.PercentOutput,0.3)
    def cimIpManuel(self):
        if self.stick.getRawButton(5) == True:
            self.cimIpMotor.set(ctre.ControlMode.PercentOutput,1)
        if self.stick.getRawButton(6) == True:
            self.cimIpMotor.set(ctre.ControlMode.PercentOutput,-1)
        if self.stick.getRawButton(5) == False and self.stick.getRawButton(6) == False:
            self.cimIpMotor.set(ctre.ControlMode.PercentOutput,0)
    
    # def cimOto(self):
    #     if self.stick.getRawButtonPressed(6) == True:
    #         while self.cimAciEncoder.getDistance() <= 7:
    #             self.cimAciMotor.set(ctre.ControlMode.PercentOutput,0.1)
    #             print(self.cimAciEncoder.getDistance())
    #             if self.stick.getRawButtonPressed(5):
    #                 break
    #         self.cimAciEncoder.reset()
    #     elif self.stick.getRawButtonPressed(7) == True:
    #         while self.cimAciEncoder.getDistance >= -7:
    #             self.cimAciMotor.set(ctre.ControlMode.PercentOutput,-0.1)
    #             print(self.cimAciEncoder.getDistance())
    #             if self.stick.getRawButtonPressed(5):
    #                 break
    #         self.cimAciEncoder.reset()
    #     elif self.stick.getRawButtonPressed(6) == False and self.stick.getRawButtonPressed(7) == False:
    #         self.cimAciMotor.set(ctre.ControlMode.PercentOutput,0)

    def driverModeEnable(self):
        if self.stick.getRawButtonPressed(9):
            self.cam.setDriverMode(1)
            self.servoMotor.set(self.servoBall)
        if self.stick.getRawButtonPressed(10):
            self.cam.setDriverMode(0)
            self.servoMotor.set(self.servoTape)
    
    def frontShooterSpeedConfig(self):
        return ((self.shooterVal * 0,83)  * 0,9)

    def rearShooterSpeedConfig(self):
        return ((self.shooterVal * 0,83) * 1,2)


    def teleopInit(self):
        pass

    def autonomousInit(self):    
        pass

    def autonomousPeriodic(self):
        print(str(self.top))
        if self.top == 0:
            self.autoAimBall()
        else:
            self.autoAimTape()

    def teleopPeriodic(self):
        print(self.top)
        self.teleopdriveMecanum()
        self.cimIpManuel()
        self.cimAciManuel()
        self.rangeToTapeFunc()
        self.driverModeEnable()
        # print(self.servoCurrent)
        if self.stick2.getRawButton(2) == True:        
            self.autoAimTape()
        if self.stick2.getRawButton(3) == True:
            self.top = self.top_alma()
        if self.stick2.getRawButton(12) == True:
          self.ust_belt1.set(ctre.ControlMode.PercentOutput,-1)
        if self.stick2.getRawButton(11) == True:
            self.alt_belt1.set(ctre.ControlMode.PercentOutput,-1)
        if self.stick2.getRawButton(12) == True:
            self.ust_belt1.set(ctre.ControlMode.PercentOutput,-1)
        if self.stick2.getRawButton(11) == True:
            self.alt_belt1.set(ctre.ControlMode.PercentOutput,-1)
        if self.stick2.getRawButton(10) == True:
            self.onShooter1.set(ctre.ControlMode.PercentOutput,0.5)
            self.onShooter2.set(ctre.ControlMode.PercentOutput,0.5)
            self.arkaShooter.set(ctre.ControlMode.PercentOutput,-0.5)
        if self.stick2.getRawButton(9) == True:
            self.onShooter1.set(ctre.ControlMode.PercentOutput,0)
            self.onShooter2.set(ctre.ControlMode.PercentOutput,0)
            self.arkaShooter.set(ctre.ControlMode.PercentOutput,0)
            self.alt_belt1.set(ctre.ControlMode.PercentOutput,0)
            self.ust_belt1.set(ctre.ControlMode.PercentOutput,0)
if __name__ == "__main__":
    wpilib.run(MyRobot)

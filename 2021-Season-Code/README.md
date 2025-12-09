# FRC 2021 Season Code: Game Piece Handling and Sensor Feedback

## 🎯 Project Summary
This code was developed for the **FRC 2021 (Infinite Recharge at Home)** challenges using **Python (WPILib TimedRobot)** structure. The primary objective was to achieve robust and reliable control over the robot's mechanical subsystems for game piece acquisition and scoring.

The code demonstrates experience in translating complex operational requirements (e.g., "Take a ball, check the color, stage it for 3.5 seconds") into real-time, event-driven software logic.

---

## 💡 Key Technical Highlights

### 1. Sequential Control Logic
The functions `ball_take()` and `ball_shoot()` utilize **nested `while` loops** and the `wpilib.Timer()` to create **state machine-like sequences**. This ensures mechanisms run in a precise order and stop only after meeting specific sensor conditions or time constraints, which is critical for mechanism reliability.

* **Demonstrated Skill:** Robust handling of multi-step, asynchronous mechanism routines.

### 2. Sensor Integration (I2C Color Sensor)
The `ball_check()` function directly interfaces with the **REV Color Sensor V3** via the **I2C bus**.

* **Function:** `ball_check()` performs **RGB Color Thresholding** to identify the presence and, implicitly, the correct color of the game piece based on defined `color.red`, `color.blue`, and `color.green` ranges.
* **Demonstrated Skill:** Low-level sensor data acquisition and implementation of sensor-based control feedback.

### 3. Dynamic Operator Control
The code provides granular control over robot parameters, moving beyond simple button mapping:

* **`shooter_dist()`**: Implements a **mode-switching system** (`mod` 1 through 4) allowing the operator to quickly select pre-calibrated `shooter_motor_speed` values for different firing distances.
* **`change_speed()`**: Enables the operator to manually increment or decrement the base drive speed (`chassis_motor_speed`) scalar for fine-tuning the chassis sensitivity during the match.

---

## ⚙️ Software and Hardware Details

| Component | WPILib Class | Purpose |
| :--- | :--- | :--- |
| **Control Structure** | `wpilib.TimedRobot` | Standard FRC periodic loop structure. |
| **Chassis Control** | `wpilib.drive.DifferentialDrive` | Implements **Arcade Drive** control. |
| **Motors** | `wpilib.PWMVictorSPX` & `SpeedControllerGroup` | Control for Drive Train, Shooter, Intake, Hopper, and Belt systems. |
| **Pneumatics** | `wpilib.DoubleSolenoid` | Controls the **Intake Deployment** and **Shooter Angle**. |
| **Timer** | `wpilib.Timer` | Used for fixed-duration sequencing (e.g., timing the ball staging phase in `ball_take`). |

***

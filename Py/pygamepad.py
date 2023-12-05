"""
Controller functions for Gran Turismo (PSX)
Written by NDR008
nadir.syedsammut@gmail.com
Development started in December 2022
"""

# https://github.com/yannbouteiller/vgamepad/blob/main/vgamepad/win/vigem_commons.py

import math

# discreteAccel & accelAndBrake & discreteSteer
# 3 controls
def disAccelandBrakeDiscSteer(gamepad, control):  # control0
    if control[0] > 0:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel
    if control[1] > 0:  # brake
        gamepad.press_button(button = 1 << 4) # brake
    else:
        gamepad.release_button(button = 1 << 4) # release brake
        
    if control[2] > 0:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[2] < 0: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
    gamepad.update()

# discreteAccel or discBrakeBrake & discreteSteer
# 2 controls
def disAccelorBrakeDiscSteer(gamepad, control):  # control1
    # print(control)
    if control[0] > 0:  # gas
        gamepad.press_button(button=1 << 5)  # accel
        gamepad.release_button(button = 1 << 4) # release brake
    elif control[0] <0 :
        gamepad.release_button(button = 1 << 5) # release accel
        gamepad.press_button(button=1 << 4)  # brake
    else:
        gamepad.release_button(button=1 << 5)  # release accel
        gamepad.release_button(button=1 << 4)  # release brake

    if control[1] > 0:  # right
        gamepad.directional_pad(direction=0x2)  # press right
    elif control[1] < 0:  # left
        gamepad.directional_pad(direction=0x6)  # press left
    else:
        gamepad.directional_pad(direction=0x8)  # nothing
    gamepad.update()
    
# discreteAccel or discBrakeBrake & discreteSteer
# 2 controls
def contAccelorBrakeContSteer(gamepad, control):  # control1.5
    accelBrake = min(control[0], 1)
    accelBrake = max(accelBrake, -1)
    gamepad.right_joystick_float(x_value_float=0, y_value_float=accelBrake)

    steer = min(control[1], 1)
    steer = max(steer, -1)
    gamepad.left_joystick_float(x_value_float=steer, y_value_float=0)
    gamepad.update()


def contAccelContSteer(gamepad, control):  # control1.5
    accelBrake = min(control[0], 1)
    accelBrake = max(accelBrake, -1)
    accelBrake = accelBrake/2 + 0.5
    gamepad.right_joystick_float(x_value_float=0, y_value_float=accelBrake)

    steer = min(control[1], 1)
    steer = max(steer, -1)
    gamepad.left_joystick_float(x_value_float=steer, y_value_float=0)
    gamepad.update()            

def disAccelnotBrakeDiscSteer(gamepad, control):  # control2
    #print(control)
    if control[0] > 0:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel   
    
    if control[1] > 0:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[1] < 0: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
    gamepad.update()        


def disAccelnotBrakeDiscSteer2(gamepad, control):  # control2.5
    #print(control)
    if control[0] > 0:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel   
    
    if control[1] > 0.3:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[1] < 0.3: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
    gamepad.update()  
    
    
def contAccelContSteer(gamepad, control): # control5
    accelBrake = min(control[0],1)
    accelBrake = max(accelBrake, -1)
    gamepad.right_joystick_float(x_value_float=0, y_value_float=accelBrake)
        
    steer = min(control[2],1)
    steer = max(steer, -1)
    gamepad.left_joystick_float(x_value_float=steer, y_value_float=0)
    gamepad.update()

# cont accelOnly   
def contAccelOnly(gamepad, control): # control6
    accelBrake = min(control[0],1)
    accelBrake = max(accelBrake, -1)
    gamepad.right_joystick_float(x_value_float=0, y_value_float=accelBrake)
    gamepad.update()          
         

def controlGamepad(gamepad, control, choice): 
    if choice==0: 
        disAccelandBrakeDiscSteer(gamepad, control)
        
    elif choice == 1:
        disAccelorBrakeDiscSteer(gamepad, control)
        
    elif choice == 1.5:
        contAccelorBrakeContSteer(gamepad, control)
    
    elif choice == 1.6:
        contAccelContSteer(gamepad, control)
        
    elif choice==2: 
        disAccelnotBrakeDiscSteer(gamepad, control)
        
    elif choice==2.5: 
        disAccelnotBrakeDiscSteer2(gamepad, control)     
  
  
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
    if control[0] > 0.5:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel
    if control[1] > 0.5:  # brake
        gamepad.press_button(button = 1 << 4) # brake
    else:
        gamepad.release_button(button = 1 << 4) # release brake
        
    if control[2] > 0.6:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[2] < 0.4: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
    gamepad.update()
        
# discreteAccel & accelAndBrake & not discreteSteer
# 3 controls
def disAccelandBrakeContSteer(gamepad, control): # control1
    if control[0] > 0.5:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel
    if control[1] > 0.5:  # brake
        gamepad.press_button(button = 1 << 4) # brake
    else:
        gamepad.release_button(button = 1 << 4) # release brake
        
    steer = min(control[2],1)
    steer = max(steer, -1)
    gamepad.left_trigger_float(x_value_float=steer)
    gamepad.update()

            
# discreteAccel & not accelAndBrake & discreteSteer
# 2 controls
def disAccelnotBrakeDiscSteer(gamepad, control): # control2
    #print(control)
    if control[0] > 0:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel   
    
    if control[1] > 0.25:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[1] < -0.25: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
    gamepad.update()        

# discreteAccel & not accelAndBrake & not discreteSteer
# 2 controls
def disAccelnotBrakeContSteer(gamepad, control): # control3
    if control[0] > 0.6:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    elif control[0] < 0.4:  # brake
        gamepad.press_button(button = 1 << 5) # brake
    else:
        gamepad.release_button(button = 1 << 4) # release brake
        gamepad.release_button(button = 1 << 5) # release accel      
        
    steer = min(control[2],1)
    steer = max(steer, -1)
    gamepad.left_trigger_float(x_value_float=steer)
    gamepad.update()                    

# not discreteAccel & discreteSteer
# 2 controls
def conAccelDisctSteer(gamepad, control): # control4
    accelBrake = min(control[0],1)
    accelBrake = max(accelBrake, -1)
    gamepad.right_joystick_float(x_value_float=0, y_value_float=accelBrake)     
    
    if control[1] > 0.6:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[1] < -0.4: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
        
    gamepad.update() 
    
# not discreteAccel & not discreteSteer
# 2 controls
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
    
def discAccelOnly(gamepad, control): # control7
    if control[0] > 0.5:  # gas
        gamepad.press_button(button = 1 << 5) # accel
    else:
        gamepad.release_button(button = 1 << 5) # release accel   
    gamepad.update()             

def controlGamepad(gamepad, control, choice):
    if choice==7:
        discAccelOnly(gamepad, control)
        
    elif choice==6:
        contAccelOnly(gamepad, control)
        
    elif choice==5: # wrong
        contAccelOnly(gamepad, control)

    elif choice==4: # wrong
        contAccelOnly(gamepad, control)
        
    elif choice==3: # wrong
        contAccelOnly(gamepad, control)        
        
    elif choice==2: 
        disAccelnotBrakeDiscSteer(gamepad, control)     
        
    elif choice==1: 
        disAccelandBrakeDiscSteer(gamepad, control)         
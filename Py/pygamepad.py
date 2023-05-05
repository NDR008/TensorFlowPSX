# https://github.com/yannbouteiller/vgamepad/blob/main/vgamepad/win/vigem_commons.py

def controlGamepad(gamepad, control):
    # This function accepts only controls between -1.0 and 1.0
    # control(gas, brake, steer) range(0,1)
    # assert all(-1.0 <= c <= 1.0 for c in control)
    if control[0] > 0:  # gas
        gamepad.press_button(button = 1 << 5) # X
    else:
        gamepad.release_button(button = 1 << 5) # release X
    if control[1] > 0:  # brake
        gamepad.press_button(button = 1 << 4) # O
    else:
        gamepad.release_button(button = 1 << 4) # release O
        
    if control[2] > 0:  # right
        gamepad.directional_pad(direction = 0x2) # press right 
    elif control[2] < 0: #left
        gamepad.directional_pad(direction = 0x6) # press left
    else:
        gamepad.directional_pad(direction = 0x8) # nothing
        
    gamepad.update()

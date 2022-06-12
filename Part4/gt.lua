hasPal = false
hasUs = false
hasJap = false

local function doCheckbox(mem, address, name, value, original, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local changed
    local check
    local tempvalue = pointer[0]
    if tempvalue == original then check = false end
    if tempvalue == value then check = true else check = false end
    changed, check = imgui.Checkbox(name, check)
    if changed then
        if check then pointer[0] = value else pointer[0] = original end
    end
end

function DrawImguiFrame()

end

-- Declare a helper function with the following arguments:
--   mem: the ffi object representing the base pointer into the main RAM
--   address: the address of the uint32_t to monitor and mutate
--   name: the label to display in the UI
--   min, max: the minimum and maximum values of the slider
local function doSliderInt(mem, address, name, min, max, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local value = pointer[0]
    local changed
    changed, value = imgui.SliderInt(name, value, min, max, '%d')
    if changed then pointer[0] = value end
end

-- Utilizing the DrawImguiFrame periodic function to draw our UI.
-- We are declaring this function global so the emulator can
-- properly call it periodically.
function DrawImguiFrame()
    local show = imgui.Begin('GT Hacking', true)
    if not show then imgui.End() return end
    local mem = PCSX.getMemPtr()

    -- All for the PAL SCES-00984 version of the game.
    -- Now calling our helper function for each of our pointer.
    if hasPal then
        doSliderInt(mem, 0x800b66ec, 'Speed1', 0, 5000, 'uint16_t*')
        doSliderInt(mem, 0x800b66ee, 'Engine Speed', 0, 12000, 'uint16_t*')
        doSliderInt(mem, 0x800b66e8, 'Gear', 0, 10, 'uint8_t*')
        doSliderInt(mem, 0x800b66fa, 'Accel0 (changes with X)', 65525, 0, 'uint16_t*')
        doSliderInt(mem, 0x800b66d9, 'Accel1 (equal to button press)', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800b66db, 'Accel2 (blips on shift)', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800b66dd, 'Brake1', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800b66df, 'Brake2', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800b66e1, 'Brake3', 0, 16, 'uint16_t*')
        doSliderInt(mem, 0x800b66d6, 'Steering', -580, 580, 'int16_t*')
        doSliderInt(mem, 0x800b6d69, 'Car Position', 1, 6, 'int16_t*')
        doCheckbox(mem, 0x800b6358, '(PAL SCES-00984) HUD', 0, 1, 'int16_t*')

    elseif hasUs then
        doCheckbox(mem, 0x800b6508, '(NTSC-U SCUS-94194) HUD', 0, 1, 'int16_t*')

    elseif hasJap then
        doCheckbox(mem, 0x800ad838, '(NTSC-J SCPS-10045) HUD', 0, 1, 'int16_t*')

    end

    -- Don't forget to close the ImGui window.
    imgui.End()

end

function myFunc()
    local reader = PCSX.getCurrentIso():createReader()
    print("GT1 region detection started!")
    local pal = reader:open('SCES_009.84;1')
    local us = reader:open('SCUS_941.94;1')
    local jap = reader:open('SCPS_100.41;1')

    hasPal = not pal:failed() -- this line crashes redux :(
    hasUs = not us:failed()
    hasJap = not jap:failed()
end

PCSX.Events.createEventListener('ExecutionFlow::Run', myFunc)

function checkValue(mem, address, value, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local tempvalue = pointer[0]
    local check = false
    if tempvalue == value then
        check = true
    end
    return check
end

function doCheckbox(mem, address, name, value, original, type)
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

-- Declare a helper function with the following arguments:
--   mem: the ffi object representing the base pointer into the main RAM
--   address: the address of the uint32_t to monitor and mutate
--   name: the label to display in the UI
--   min, max: the minimum and maximum values of the slider
function doSliderInt(mem, address, name, min, max, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local value = pointer[0]
    local changed
    changed, value = imgui.SliderInt(name, value, min, max, '%d')
    if changed then pointer[0] = value end
end

function readValue(mem, address, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local value = pointer[0]
    return value
end

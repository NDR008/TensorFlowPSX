carData = ''

function openData()
    print("open car data")
    carData = ''
    local file = Support.File.open("car.csv", "CREATE")
    file:close()
end

function writeData()
    local accel = readValue(mem, 0x800b66d8, 'int16_t*')
    local clutch = readValue(mem, 0x800b6d63, 'uint16_t*')
    local rpm = readValue(mem, 0x800b66ee, 'uint16_t*')
    local boost = readValue(mem, 0x800b66f8, 'uint16_t*')
    local speed = readValue(mem, 0x800b66ec, 'uint16_t*')
    -- local z = readValue(mem, 0x800b670c, 'int32_t*')
    
    local strCarDrive = tostring(accel) .. ',' .. tostring(clutch) .. ',' .. tostring(rpm) .. ',' .. tostring(boost) .. ',' .. tostring(speed) .. '\n'
    carData = carData .. strCarDrive
    -- print(strDrive)
end

function closeData()
    appendData()
end

function appendData()
    file = Support.File.open("car.csv", "READWRITE")
    file:write(carData)
    file:close()
    print("close car")
end
driveRecording = ''

function openRecord()
    print("open record")
    coordDrive = ''
    local file = Support.File.open("drive.csv", "CREATE")
    file:close()
end

function writeRecord()
    local lap = readValue(mem, 0x800b6700, 'int32_t*')
    local x = readValue(mem, 0x800b6704, 'int32_t*')
    local y = readValue(mem, 0x800b6708, 'int32_t*')
    local speed = readValue(mem, 0x800b66ec, 'uint16_t*')
    -- local z = readValue(mem, 0x800b670c, 'int32_t*')
    
    local strDrive = tostring(lap) .. ',' .. tostring(x) .. ',' .. tostring(y) .. ',' .. tostring(speed) .. '\n'
    driveRecording = driveRecording .. strDrive
    strDrive = ''
    -- print(strDrive)
end

function closeRecord()
    appendCoordDrive()
end

function appendCoordDrive()
    print("SAVE DRIVE")
    file = Support.File.open("drive.csv", "READWRITE")
    file:write(driveRecording)
    file:close()
    print("close record")
end
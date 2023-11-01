coordDrive = ''
indexDrive = 0

function openRecord()
    print("open record")
    local file = Support.File.open("drive.csv", "CREATE")
    file:close()
end

function writeRecord()
    -- Front Left
    local lap = readValue(mem, 0x800b6700, 'int32_t*')
    local x = readValue(mem, 0x800b6704, 'int32_t*')
    local y = readValue(mem, 0x800b6708, 'int32_t*')
    -- local z = readValue(mem, 0x800b670c, 'int32_t*')
    
    local strDrive = tostring(lap) .. ',' .. tostring(x) .. ',' .. tostring(y) .. '\n'
    coordDrive = coordDrive .. strDrive
    print(strDrive)
end

function closeRecord()
    appendCoordDrive()
end

function appendCoordDrive()
    file = Support.File.open("drive.csv", "READWRITE")
    file:write(coordDrive)
    file:close()
    print("close record")
end
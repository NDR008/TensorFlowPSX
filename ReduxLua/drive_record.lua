coordDrive = ''
lastStrDrive = ''
indexDrive = 0

SingleLap = False

function openRecord()
    print("open")
    local file = Support.File.open("drive.csv", "CREATE")
    file:close()
end

local last_lap = 0
function writeRecord()
    -- Front Left
    local lap = readValue(mem, 0x800b6700, 'int32_t*')
    local x = readValue(mem, 0x800b6704, 'int32_t*')
    local y = readValue(mem, 0x800b6708, 'int32_t*')
    -- local z = readValue(mem, 0x800b670c, 'int32_t*')
    
    local strDrive = tostring(x) .. ',' .. tostring(y) .. '\n'
    if strDrive ~= lastStr then
        indexDrive = indexDrive + 1
        if index % 1 == 0 then
            coordDrive = coordDrive .. strDrive
            lastStrDrive = strDrive
        end
    end
end

function closeRecord()
    appendCoordDrve()
end

function appendCoordDrve()
    file = Support.File.open("hs.csv", "READWRITE")
    file:write(coordDrive)
    file:close()
end
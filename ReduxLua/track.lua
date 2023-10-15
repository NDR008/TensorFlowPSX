coord = ''
lastStr = ''
index = 0

SingleLap = False

function openTrack()
    print("open")
    local file = Support.File.open("hs.csv", "CREATE")
    file:close()
end

local last_lap = 0
function writeTrack()
    -- Front Left
    local lap = readValue(mem, 0x800b6700, 'int32_t*')
    local x = readValue(mem, 0x800b6704, 'int32_t*')
    local y = readValue(mem, 0x800b6708, 'int32_t*')
    -- local z = readValue(mem, 0x800b670c, 'int32_t*')

    if readValue(mem, 0x800b66ec, 'uint16_t*') > 100 then
        setValue(mem, 0x800b66ee, 1200, 'uint16_t*')
    end
    
    if SingleLap then
        if (lap - last_lap) == 1 then
            print(x,y)
        end

        if lap == 1 then
            str = tostring(x) .. ',' .. tostring(y) .. '\n'
            if str ~= lastStr then
                index = index + 1
                if index % 1 == 0 then
                    coord = coord .. str
                    lastStr = str
                end
            end  
        end
        last_lap = lap

    else
        str = tostring(x) .. ',' .. tostring(y) .. '\n'
        if str ~= lastStr then
            index = index + 1
            if index % 1 == 0 then
                coord = coord .. str
                lastStr = str
            end
        end
    end
end

function closeTrack()
    appendCoord()
end

function appendCoord()
    file = Support.File.open("hs.csv", "READWRITE")
    file:write(coord)
    file:close()
end
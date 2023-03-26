coord = ''
lastStr = ''
index = 0

function openTrack()
    print("open")
    local file = Support.File.open("track.csv", "CREATE")
    file:close()
end

function writeTrack()
    -- Front Left
    local lap = readValue(mem, 0x800b6700, 'int32_t*')
    local x = readValue(mem, 0x800b6704, 'int32_t*')
    local y = readValue(mem, 0x800b6708, 'int32_t*')
    local z = readValue(mem, 0x800b670c, 'int32_t*')
    if lap == 1 then
        str = tostring(x) .. ',' .. tostring(y) .. '\n'
        if str ~= lastStr then
            index = index + 1
        end
        if index % 10 == 0 then
            coord = coord .. str
        end
        lastStr = str
    end
end

function closeTrack()
    appendCoord()
end

function appendCoord()
    file = Support.File.open("track.csv", "READWRITE")
    file:write(coord)
    file:close()
end
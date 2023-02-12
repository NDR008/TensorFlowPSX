coord = ''

function openTrack()
    print("open")
    local file = Support.File.open("track.csv", "CREATE")
    file:close()
end

function writeTrack()
    local y = readValue(mem, 0x800b6708, 'int32_t*')
    local x = readValue(mem, 0x800b6704, 'int32_t*')
    str = tostring(x) .. ',' .. tostring(y) .. '\n'
    coord = coord .. str
end

function closeTrack()
    appendCoord()
end

function appendCoord()
    file = Support.File.open("track.csv", "READWRITE")
    file:write(coord)
    file:close()
end
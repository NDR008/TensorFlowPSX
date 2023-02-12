local coord = {}

function openTrack()
    print("open")
    local file = Support.File.open("track.txt", "CREATE")
    file:close()
    file = Support.File.open("track.txt", "READWRITE")
    file:write("BOO")
    file:close()
end

function writeTrack()
    
end

function closeTrack()
    print("closed")
end

local function appendCoord()
    local file = Support.File.open("track.txt", "CREATE")
    file:close()
    file = Support.File.open("track.txt", "READWRITE")
    file:write("BOO")
    file:close()
end
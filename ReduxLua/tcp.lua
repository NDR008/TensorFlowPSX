local pb = require('pb')
local protoc = require('protoc')

local function read_file_as_string(filename)
    local file = Support.File.open(filename)
    local buffer = file:read(tonumber(file:size()))
    file:close()
    return tostring(buffer)
end

local function check_load(chunk)
    local pbdata = protoc.new():compile(chunk)
    local ret, offset = pb.load(pbdata)
    if not ret then
        error("load error at " .. offset ..
            "\nproto: " .. chunk ..
            "\ndata: " .. buffer(pbdata):tohex())
    end
end

local proto_file = read_file_as_string('game.proto')
check_load(proto_file)


-- To clean later

HEADER = 10
counter = 0

local localRaceStart = 99

function netTCP(netChanged, netCheck)
    if netChanged then
        if netCheck then
            client = Support.File.uvFifo("127.0.0.1", 9999)
        else
            client:close()
        end
    elseif netCheck then
        client:write("P")
        local screen = PCSX.GPU.takeScreenShot()
        screen.data = tostring(screen.data)
        screen.bpp = tonumber(screen.bpp)
        local enc_bytes = assert(pb.encode("GT.Screen", screen))
        client:write(#enc_bytes)
        print(#enc_bytes)
        client:write(enc_bytes)
    else
    end
end

function overwriteFlag(giveMeData)
    localRaceStart = giveMeData
end

-- Protobuf related

local pb = require('pb')
local protoc = require('protoc')
local frames = 0
local frames_needed = 2

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

-- REDUX related
local mem = PCSX.getMemPtr()

local function readValue(mem, address, type)
    address = bit.band(address, 0x1fffff)
    local pointer = mem + address
    pointer = ffi.cast(type, pointer)
    local value = pointer[0]
    return value
end

local function readGameState()
    local raceStart = readValue(mem, 0x800b6d60, 'uint8_t*')
    local raceMode = readValue(mem, 0x800b6226, 'uint8_t*')
    local racing = readValue(mem, 0x8008df72, "int8_t*")
    if racing ~= 58 then
        return 4 -- not in race
    elseif raceStart == 1 then
        return 0 -- race finished
    elseif raceMode == 0 then
        return 1 -- racing
    else
        return 2 -- race finished
    end
end

-- TCP related

function netTCP(netChanged, netCheck)
    if netChanged then
        if netCheck then
            client = Support.File.uvFifo("127.0.0.1", 9999)
        else
            client:close()
        end
    elseif netCheck then
        frames = frames + 1
        if (frames % frames_needed) == 0 then
            local screen = PCSX.GPU.takeScreenShot()
            screen.data = tostring(screen.data)
            screen.bpp = tonumber(screen.bpp)
            -- print(screen.bpp, screen.width, screen.height)
            local enc_Screenbytes = assert(pb.encode("GT.Screen", screen))
            -- bytes = string.format("%08d", #enc_bytes)
            -- client:write(bytes)
            -- print(#enc_bytes, bytes)
            client:write("P")
            client:writeU32(#enc_Screenbytes)
            -- print(#enc_bytes)
            client:write(enc_Screenbytes)
            -- print(checkNumberMessages)
            -- checkNumberMessages = checkNumberMessages + 1
            local gameState = {}
            gameState['raceState'] = readGameState()
            local enc_GSbytes = assert(pb.encode("GT.GameState", gameState))
            client:writeU32(#enc_GSbytes)
            -- print(#enc_bytes)
            client:write(enc_GSbytes)
            --print(enc_GSbytes)
        end
    end

end

function overwriteFlag(giveMeData)
    localRaceStart = giveMeData
end

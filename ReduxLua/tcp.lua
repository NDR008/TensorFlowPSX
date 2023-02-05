-- Protobuf related

local pb = require('pb')
local protoc = require('protoc')
local frames = 0
local frames_needed = 2
local gameState = {}
local vehicleState = {}

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
        return 6 -- not in race
    elseif raceStart == 1 then
        return 1 -- race finished
    elseif raceMode == 0 then
        return 2 -- racing
    else
        return 3 -- race finished
    end
end

local function readVehicleState()
    vehicleState = {}
    vehicleState['engSpeed'] = readValue(mem, 0x800b66ee, 'uint16_t*')
    vehicleState['engBoost'] = readValue(mem, 0x800b66f8, "uint16_t*")
    vehicleState['engGear'] = readValue(mem, 0x800b66e8, "uint8_t*")
    vehicleState['speed'] = readValue(mem, 0x800b66ec, 'uint8_t*')
    vehicleState['steer'] = readValue(mem, 0x800b66d6, "int16_t*")
    vehicleState['pos'] = readValue(mem, 0x800b6d69, "int16_t*")
    return vehicleState
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
            client:write("P")
            local screen = PCSX.GPU.takeScreenShot()
            screen.data = tostring(screen.data)
            screen.bpp = tonumber(screen.bpp)
            local enc_Screenbytes = assert(pb.encode("GT.Screen", screen))
            client:writeU32(#enc_Screenbytes)
            client:write(enc_Screenbytes)

            gameState['raceState'] = readGameState()
            local enc_GSbytes = assert(pb.encode("GT.GameState", gameState))
            client:writeU32(#enc_GSbytes)
            client:write(enc_GSbytes)

            if gameState['raceState'] < 6 then
                client:write("R")
                vehicleState = readVehicleState()
                local enc_VSbytes = assert(pb.encode("GT.Vehicle", vehicleState))
                client:writeU32(#enc_VSbytes)
                client:write(enc_VSbytes)
            else
                client:write("N")
            end
        end
    end

end

function overwriteFlag(giveMeData)
    localRaceStart = giveMeData
end

-- Protobuf related
local pb = require('pb')
local protoc = require('protoc')
local frames = 0
local frames_needed = 1
local obs = {}
local dieing = 0

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

local function readGameState()
    local gameState = {}
    local raceStart = readValue(mem, 0x800b6d60, 'uint8_t*')
    local raceMode = readValue(mem, 0x800b6226, 'uint8_t*')
    local racing = readValue(mem, 0x8008df72, "int8_t*")
    if racing ~= 58 then
        gameState['raceState'] = 6 -- not in race
    elseif raceStart == 1 then
        gameState['raceState'] = 1 -- race finished
    elseif raceMode == 0 then
        gameState['raceState'] = 2 -- racing
    else
        gameState['raceState'] = 3 -- race finished
    end
    return gameState
end

local function readVehicleState()
    local vehicleState = {}
    vehicleState['engSpeed'] = readValue(mem, 0x800b66ee, 'uint16_t*')
    vehicleState['engBoost'] = readValue(mem, 0x800b66f8, "uint16_t*")
    vehicleState['engGear'] = readValue(mem, 0x800b66e8, "uint8_t*")
    vehicleState['speed'] = readValue(mem, 0x800b66ec, 'uint8_t*')
    vehicleState['steer'] = readValue(mem, 0x800b66d6, "int16_t*")
    vehicleState['pos'] = readValue(mem, 0x800b6d69, "int16_t*")
    return vehicleState
end

local function readVehiclePositon()
    local pos = {}
    pos['x'] = readValue(mem, 0x800b6704, 'int32_t*')
    pos['y'] = readValue(mem, 0x800b6708, 'int32_t*')
    pos['z'] = readValue(mem, 0x800b670c, 'int32_t*')
    return pos
end
-- TCP related

function netTCP(netChanged, netStatus)
    if netChanged then
        if netStatus then
            client = Support.File.uvFifo("127.0.0.1", 9999)
            dieing = 0
            frames = 0
        else
            client:close()
            dieing = 0
        end
    elseif netStatus then
        frames = frames + 1
        if (frames % frames_needed) == 0 then
            client:write("P")
            local screen = PCSX.GPU.takeScreenShot()
            screen.data = tostring(screen.data)
            screen.bpp = tonumber(screen.bpp)
            local gameState = readGameState()
            local vehicleState
            local pos = readVehiclePositon()
            if gameState['raceState'] < 6 then
                vehicleState = readVehicleState()
            end

            obs['SS'] = screen
            obs['GS'] = gameState
            obs['VS'] = vehicleState
            obs['frame'] = frames
            obs['pos'] = pos

            local test = assert(pb.encode("GT.Observation", obs))
            client:writeU32(#test)
            client:write(test)
            if client:readU16() == 1 then
                dieing = math.max(0, (dieing - 2))
            else
                dieing = dieing + 1
            end
        end
    end
    if dieing == 30 then
        print("Could not find a server")
        client:close()
        dieing = 0
        netStatus = false
        return netStatus
    else
        return netStatus
    end
end
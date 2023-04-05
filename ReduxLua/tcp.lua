-- Protobuf related
local pb = require('pb')
local protoc = require('protoc')
local frames = 0
local frames_needed = 1
local obs = {}
local dieing = 0
local client = nil
local reconnectTry = false

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

function grabGameData()
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

    GlobalData = assert(pb.encode("GT.Observation", obs))
end

function netTCP(netChanged, netStatus)
    local turnOn = (reconnectTry or netChanged)
    if turnOn then
        if netStatus then
            print("trying to reacher server")
            client = Support.File.uvFifo("127.0.0.1", 9999)
            frames = 0
            dieing = 0
            reconnectTry = false
        else
            client:close()
            dieing = 0
        end
    elseif netStatus then
        local readVal = client:readU16()
        local ready = false
        if readVal == 1 then
            ready = true
        elseif readVal == 2 then
            local file = Support.File.open("arc5.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
            ready = true
        end
        frames = frames + 1
        local screen = PCSX.GPU.takeScreenShot()
        if (frames % frames_needed) == 0 and ready then
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
            local chunk = assert(pb.encode("GT.Observation", obs))
            client:write("P")
            client:writeU32(#chunk)
            client:write(chunk)
        end
    end
    -- print(dieing)
end

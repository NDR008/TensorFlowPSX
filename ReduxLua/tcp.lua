-- Protobuf related
local pb = require('pb')
local protoc = require('protoc')
local frames = 0
local frames_needed = 1
local obs = {}
local client = nil
local reconnectTry = false
local CurrentPos = 0
local maxLostPings = 50000
local currentMissedPings = 0

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
        gameState['raceState'] = 5 -- not in race
    elseif raceStart == 1 then
        gameState['raceState'] = 1 -- race start
    elseif raceMode == 0 then
        gameState['raceState'] = 2 -- racing
    else
        gameState['raceState'] = 3 -- race finished
    end
    return gameState
end

local function readCollission()
    local collisionState = readValue(mem, 0x800b66e9, 'int8_t*')
    local collisionValue = readValue(mem, 0x800b66ea, 'int8_t*')

    -- print("pre", HeldCollState, collisionState, collisionValue)
    if collisionValue > 0 and collisionState > 0 then
        HeldCollState = collisionState
    elseif collisionValue == 0 then
        HeldCollState = 0
    end
    -- print("pos", HeldCollState, collisionState, collisionValue)
    return HeldCollState
end

local function readVehicleState()
    local vehicleState = {}
    vehicleState['engSpeed'] = readValue(mem, 0x800b66ee, 'uint16_t*')
    vehicleState['engBoost'] = readValue(mem, 0x800b66f8, "uint16_t*")
    vehicleState['engGear'] = readValue(mem, 0x800b66e8, "uint8_t*")
    vehicleState['speed'] = readValue(mem, 0x800b66ec, 'uint8_t*')
    vehicleState['steer'] = readValue(mem, 0x800b66d6, "int16_t*")
    vehicleState['pos'] = readValue(mem, 0x800b6d69, "int16_t*")
    vehicleState['eClutch'] = readValue(mem, 0x800b6d63, "uint16_t*")
    vehicleState['fLeftSlip '] =readValue(mem, 0x800b674e,'uint8_t*')
    vehicleState['fRightSlip'] =readValue(mem, 0x800b6792,'uint8_t*')
    vehicleState['rLeftSlip'] = readValue(mem, 0x800b67d6,'uint8_t*')
    vehicleState['rRightSlip']= readValue(mem, 0x800b681a,'uint8_t*')
    vehicleState['fLWheel'] =readValue(mem, 0x800b6778, 'int8_t*')
    vehicleState['fRWheel'] =readValue(mem, 0x800b67bc, 'int8_t*')
    vehicleState['rLWheel'] =readValue(mem, 0x800b6800, 'int8_t*')
    vehicleState['rRWheel'] =readValue(mem, 0x800b6844, 'int8_t*')
    vehicleState['vColl'] = readCollission()
    return vehicleState
end

local function readVehiclePositon()
    local posVect = {}
    posVect['x'] = readValue(mem, 0x800b6704, 'int32_t*')
    posVect['y'] = readValue(mem, 0x800b6708, 'int32_t*')
    -- posVect['z'] = readValue(mem, 0x800b670c, 'int32_t*')
    return posVect
end
-- TCP related



function grabGameData()
    local screen = PCSX.GPU.takeScreenShot()
    screen.data = tostring(screen.data)
    screen.bpp = tonumber(screen.bpp)
    local gameState = readGameState()
    local vehicleState = readVehicleState()
    local posVect = readVehiclePositon()

    -- will offload the track position calculations to Python
    --[[
    if gameState['raceState'] < 6 then
        vehicleState = readVehicleState()
        lap = readValue(mem, 0x800b6700, 'int8_t*')
        if lap == 0 and gameState['raceState'] == 1 then
            CurrentPos = 0
            obs['trackID'] = CurrentPos
        else
            local x = readValue(mem, 0x800b6704, 'int32_t*')
            local y = readValue(mem, 0x800b6708, 'int32_t*')
            CurrentPos = closestPoints(Xc, Yc, x, y) + (lap - 1) * TrackMaxID
            obs['trackID'] = CurrentPos
        end
    else
        obs['trackID'] = 0
    end
    ]]--

    obs['SS'] = screen
    obs['GS'] = gameState
    obs['VS'] = vehicleState
    obs['frame'] = frames
    obs['posVect'] = posVect
    local vDir = readValue(mem, 0x800b6e74, 'int16_t*')
    if vDir >= 1 then
        vDir = 1
    end
    obs['drivingDir'] = vDir
    GlobalData = assert(pb.encode("GT.Observation", obs))
end

function netTCP(netChanged, netStatus)
    -- this seciton is messy
    local turnOn = (reconnectTry or netChanged)
    if turnOn then
        if netStatus then
            client = Support.File.uvFifo("127.0.0.1", 9999)
            frames = 0
            reconnectTry = false
        else
            client:close()
        end
    -- main loop    
    elseif netStatus then
        local readVal = client:readU32() -- receive a 1 or 2 had a bug till U32 not U16 14.10!
        local ready = false
        -- 1 is the main loop for frame capture
        if readVal == 1 then
            ready = true
            currentMissedPings = 0
        -- 2 is for loading a savestate    
        elseif readVal == 8 + 64 then -- MR2 at Drag
            lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
            print("lapt_time ", lapTime)
            local file = Support.File.open("mr2_1_0_0_0.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
        elseif readVal == 24 + 64 then -- Supra at Drag
            lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
            print("lapt_time ", lapTime)
            local file = Support.File.open("Sup_1_0_0_0.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
        elseif readVal == 0 + 64 then -- MR2 at HS
            lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
            print("lapt_time ", lapTime)
            local file = Support.File.open("mr2_0_0_0_0.slice", "READ")
            PCSX.loadSaveState(file)
            file:close()
        -- elseif readVal == 1 then
        --     lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
        --     print(lapTime)
        --     local file = Support.File.open("arc5.slice", "READ")
        --     PCSX.loadSaveState(file)
        --     file:close()
        -- elseif readVal == 3 then
        --     lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
        --     print(lapTime)
        --     local file = Support.File.open("mr2_400.slice", "READ")
        --     PCSX.loadSaveState(file)
        --     file:close()
        -- elseif readVal == 4 then
        --     lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
        --     print(lapTime)
        --     local file = Support.File.open("sim5.slice", "READ")
        --     PCSX.loadSaveState(file)
        --     file:close()
        -- elseif readVal == 5 then
        --     lapTime = readValue(mem, 0x80093bc8, 'uint32_t*')
        --     print(lapTime)
        --     local file = Support.File.open("sim6.slice", "READ")
        --     print("loaded sim6.slice")
        --     PCSX.loadSaveState(file)
        --     file:close()
        else
            currentMissedPings = currentMissedPings + 1
        end

        if currentMissedPings > maxLostPings then
            currentMissedPings = 0
            reconnectTry = true
            print("Retry to connect to server")
            ready = false
            client:close()
        end
        -- keep track of the number of frames rendered
        frames = frames + 1

        -- if this is the nth frame and we have previously received a 1
        if (frames % frames_needed) == 0 and ready then
            grabGameData() -- take screenshot, encode it with protobuf and get ready to send it
            client:write("P") -- send "P" for the python server to know we are ready
            client:writeU32(#GlobalData) -- send the size of the chunk of data
            client:write(GlobalData) -- send the actual chunk of data
            client:write("D")            -- send "P" for the python server to know we are ready
        end
    end
end

-- protobuf

local pb = require "pb"
local protoc = require "protoc"

-- load schema from text (just for demo, use protoc.new() in real world)
assert(protoc:load [[
    enum BPP {
        BPP_16 = 0;
        BPP_24 = 1;
    }

    enum gameState {
        loading = 0;
        pre_start = 1;
        race = 2;
        race_finished =3;
    }

    message observation {
        int32 debug = 1;
        message vehicle {
            int32 current_speed = 1;
            int32 current_steering = 2;
            int32 current_accel = 3;
            int32 current_brake = 4;
        }
        message screen {
            int32 width = 1;
            int32 height = 2;
            BPP bpp = 3;
            bytes image_data = 4;
        }
    }
    ]])

-- lua table data
local data = {
    debug   = 99,
    vehicle = {
        current_speed = 100,
        current_accel = 0
    }
}

local bytes = assert(pb.encode("observation", data))
print(pb.tohex(bytes))

local data2 = assert(pb.decode("observation", bytes))
print(require "serpent".block(data2))



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
        --client:write("PCSX.SIO0.slots[1].pads[1].getButton(PCSX.CONSTS.PAD.BUTTON.CROSS)")
        data = 0
        client:write("A")
        client:write(localRaceStart)
        data = client:readU8()
        print(counter, data)
        if data == 1 then
            PCSX.SIO0.slots[1].pads[1].setOverride(PCSX.CONSTS.PAD.BUTTON.CROSS)
            PCSX.SIO0.slots[1].pads[1].setOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE)
            counter = counter + 1
        elseif data == 2 then
            PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CROSS)
        end
        a = PCSX.GPU.takeScreenShot()
        -- print(a.width, a.height, a.bpp)
        -- client:write(a.width)
    else
        PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CROSS)
        PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE)
    end
end

function overwriteFlag(giveMeData)
    localRaceStart = giveMeData
end

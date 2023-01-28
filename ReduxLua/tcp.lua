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
        print(a.width, a.height, a.bpp)
        -- client:write(a.width)
    else
        PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CROSS)
        PCSX.SIO0.slots[1].pads[1].clearOverride(PCSX.CONSTS.PAD.BUTTON.CIRCLE)
    end
end

function overwriteFlag(giveMeData)
    localRaceStart = giveMeData
end